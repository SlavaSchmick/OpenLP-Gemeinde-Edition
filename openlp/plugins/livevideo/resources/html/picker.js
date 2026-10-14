/**
 * picker.js drives the preview of the live video source dialog. It finds the video inputs and shows the picture of
 * the selected one, the same way the display does, and reports back to the dialog through the "pickerBridge" object.
 */

/**
 * Normalise a video device label for comparison, see display.js
 */
function _normaliseDeviceLabel(label) {
  return (label || "").replace(/\s*\([0-9a-f]{4}:[0-9a-f]{4}\)\s*$/i, "").trim().toLowerCase();
}

/**
 * Stop all the tracks of a media stream, which releases the device
 */
function _stopMediaStream(stream) {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }
}

/**
 * Translate a getUserMedia() error into a reason the dialog understands
 */
function _getFailureReason(error) {
  switch (error && error.name) {
    case "NotFoundError":
    case "OverconstrainedError":
      return "not-connected";
    case "NotReadableError":
    case "TrackStartError":
    case "AbortError":
      return "in-use";
    case "NotAllowedError":
    case "SecurityError":
      return "not-allowed";
    default:
      return "error";
  }
}

var LiveVideoPicker = {
  _bridge: null,
  _stream: null,
  _source: null,
  _request: 0,
  _canRevealLabels: true,

  /**
   * Connect to the dialog
   */
  init: function () {
    new QWebChannel(qt.webChannelTransport, function (channel) {
      LiveVideoPicker._bridge = channel.objects.pickerBridge;
      if (navigator.mediaDevices && navigator.mediaDevices.addEventListener) {
        navigator.mediaDevices.addEventListener("devicechange", function () {
          LiveVideoPicker._canRevealLabels = true;
          LiveVideoPicker.refreshDevices();
        });
      }
      LiveVideoPicker._bridge.pageReady();
    });
  },

  /**
   * Find the connected video inputs and send their labels to the dialog
   */
  refreshDevices: function () {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      LiveVideoPicker._bridge.setDevices([]);
      return;
    }
    LiveVideoPicker._getVideoInputs()
      .then(function (inputs) {
        var labels = [];
        inputs.forEach(function (input) {
          if (input.label && labels.indexOf(input.label) < 0) {
            labels.push(input.label);
          }
        });
        LiveVideoPicker._bridge.setDevices(labels);
      })
      .catch(function (error) {
        console.warn("Unable to find video inputs: " + error);
        LiveVideoPicker._bridge.setDevices([]);
      });
  },

  /**
   * Get the video inputs. Labels are only revealed once a device has been opened, so if they are hidden the first
   * device that can be opened is opened briefly.
   * @returns {Promise<MediaDeviceInfo[]>}
   */
  _getVideoInputs: function () {
    var listInputs = function () {
      return navigator.mediaDevices.enumerateDevices().then(devices => devices.filter(device => device.kind == "videoinput"));
    };
    return listInputs().then(function (inputs) {
      if (!inputs.some(input => !input.label) || !LiveVideoPicker._canRevealLabels) {
        return inputs;
      }
      LiveVideoPicker._canRevealLabels = false;
      var revealWith = function (index) {
        var constraints = {audio: false, video: index < inputs.length ? {deviceId: {exact: inputs[index].deviceId}} : true};
        return navigator.mediaDevices.getUserMedia(constraints).then(_stopMediaStream).catch(function (error) {
          if (index < inputs.length) {
            return revealWith(index + 1);
          }
          throw error;
        });
      };
      return revealWith(0).then(listInputs, () => inputs);
    });
  },

  /**
   * Show the picture of a source. When only the scaling or mirroring changed, the device keeps running.
   * @param {Object} source - The source, see Display.setLiveVideo() in display.js
   */
  preview: function (source) {
    var request = ++LiveVideoPicker._request;
    var previous = LiveVideoPicker._source;
    LiveVideoPicker._source = source;
    LiveVideoPicker._applyStyle(source);
    var isSameCapture = previous && LiveVideoPicker._stream &&
      ["deviceLabel", "width", "height", "frameRate"].every(key => previous[key] === source[key]);
    if (isSameCapture) {
      return;
    }
    LiveVideoPicker._stopStream();
    if (!source.deviceLabel) {
      LiveVideoPicker._setStatus("");
      return;
    }
    LiveVideoPicker._setStatus((source.strings || {}).connecting);
    LiveVideoPicker._getVideoInputs()
      .then(function (inputs) {
        var wanted = _normaliseDeviceLabel(source.deviceLabel);
        var device = inputs.find(input => _normaliseDeviceLabel(input.label) == wanted);
        if (!device) {
          var error = new Error("The video input is not connected");
          error.name = "NotFoundError";
          throw error;
        }
        var video = {deviceId: {exact: device.deviceId}};
        if (source.width && source.height) {
          video.width = {ideal: source.width};
          video.height = {ideal: source.height};
        }
        if (source.frameRate) {
          video.frameRate = {ideal: source.frameRate};
        }
        return navigator.mediaDevices.getUserMedia({audio: false, video: video});
      })
      .then(function (stream) {
        if (request != LiveVideoPicker._request) {
          _stopMediaStream(stream);
          return;
        }
        LiveVideoPicker._stream = stream;
        var videoElement = document.getElementById("preview");
        videoElement.srcObject = stream;
        var playing = videoElement.play();
        if (playing && playing.catch) {
          playing.catch(function (error) {
            if (error.name != "AbortError") {
              console.warn("Unable to play the preview: " + error);
            }
          });
        }
        var track = stream.getVideoTracks()[0];
        track.addEventListener("ended", function () {
          if (LiveVideoPicker._stream === stream) {
            LiveVideoPicker._stopStream();
            LiveVideoPicker._setStatus((source.strings || {}).noSignal);
            LiveVideoPicker._bridge.previewFailed("not-connected");
          }
        });
        var settings = track.getSettings ? track.getSettings() : {};
        LiveVideoPicker._setStatus(null);
        LiveVideoPicker._bridge.previewStarted(settings.width || 0, settings.height || 0, settings.frameRate || 0);
      })
      .catch(function (error) {
        if (request != LiveVideoPicker._request) {
          return;
        }
        console.warn("Unable to preview \"" + source.deviceLabel + "\": " + error);
        LiveVideoPicker._setStatus((source.strings || {}).noSignal);
        LiveVideoPicker._bridge.previewFailed(_getFailureReason(error));
      });
  },

  /**
   * Take a still image of the picture, as it would look on the screen, for the thumbnail of the source
   * @returns {string|null} The image as a data URL, or null if there is no picture
   */
  takeSnapshot: function () {
    var videoElement = document.getElementById("preview");
    if (!LiveVideoPicker._stream || !videoElement.videoWidth || !videoElement.videoHeight) {
      return null;
    }
    var canvas = document.createElement("canvas");
    canvas.width = 320;
    canvas.height = 180;
    var context = canvas.getContext("2d");
    context.fillStyle = "#000";
    context.fillRect(0, 0, canvas.width, canvas.height);
    var scaleMode = (LiveVideoPicker._source && LiveVideoPicker._source.scaleMode) || "contain";
    var width = canvas.width;
    var height = canvas.height;
    if (scaleMode != "fill") {
      var pick = scaleMode == "cover" ? Math.max : Math.min;
      var scale = pick(canvas.width / videoElement.videoWidth, canvas.height / videoElement.videoHeight);
      width = videoElement.videoWidth * scale;
      height = videoElement.videoHeight * scale;
    }
    if (LiveVideoPicker._source && LiveVideoPicker._source.mirror) {
      context.translate(canvas.width, 0);
      context.scale(-1, 1);
    }
    context.drawImage(videoElement, (canvas.width - width) / 2, (canvas.height - height) / 2, width, height);
    return canvas.toDataURL("image/jpeg", 0.85);
  },

  /**
   * Stop the preview and release the device
   */
  stop: function () {
    LiveVideoPicker._request++;
    LiveVideoPicker._source = null;
    LiveVideoPicker._stopStream();
    LiveVideoPicker._setStatus("");
  },

  _stopStream: function () {
    _stopMediaStream(LiveVideoPicker._stream);
    LiveVideoPicker._stream = null;
    document.getElementById("preview").srcObject = null;
  },

  _applyStyle: function (source) {
    var videoElement = document.getElementById("preview");
    videoElement.classList.toggle("fit-cover", source.scaleMode == "cover");
    videoElement.classList.toggle("fit-fill", source.scaleMode == "fill");
    videoElement.classList.toggle("mirror", !!source.mirror);
  },

  /**
   * Show a status text over the preview
   * @param {string|null} text - The text, or null when the picture is showing
   */
  _setStatus: function (text) {
    document.body.classList.toggle("no-picture", text !== null);
    document.getElementById("status").textContent = text || "";
  }
};

window.addEventListener("load", LiveVideoPicker.init);
