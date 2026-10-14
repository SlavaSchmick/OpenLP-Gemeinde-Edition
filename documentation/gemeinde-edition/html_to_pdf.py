"""Print an HTML file to an A4 PDF with QtWebEngine. Usage: python html_to_pdf.py <html> <pdf>"""
import sys
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets

source, target = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
app = QtWidgets.QApplication(sys.argv)
page = QtWebEngineWidgets.QWebEnginePage()


def on_loaded(ok):
    if not ok:
        print('Laden fehlgeschlagen')
        app.exit(1)
        return
    layout = QtGui.QPageLayout(QtGui.QPageSize(QtGui.QPageSize.A4), QtGui.QPageLayout.Portrait,
                               QtCore.QMarginsF(0, 0, 0, 0))
    page.printToPdf(str(target), layout)


def on_printed(path, ok):
    print('PDF erstellt' if ok else 'PDF fehlgeschlagen', path)
    app.exit(0 if ok else 1)


page.loadFinished.connect(on_loaded)
page.pdfPrintingFinished.connect(on_printed)
page.load(QtCore.QUrl.fromLocalFile(str(source)))
sys.exit(app.exec())
