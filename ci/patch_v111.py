from pathlib import Path
import sys
assets=Path(sys.argv[1] if len(sys.argv)>1 else 'app/src/main/assets')
index=assets/'index.html'
html=index.read_text()
html=html.replace('<label class="btn ghost fileBtn">Import CSV<input type="file" id="importInput" accept=".csv,text/csv" hidden></label>','<label class="btn ghost fileBtn">Import CSV<input type="file" id="importInput" accept=".csv,text/csv,text/plain,application/csv,application/vnd.ms-excel" hidden></label>')
needle='<script src="v11-ui.js"></script>'
if needle not in html: raise SystemExit('v11-ui script tag missing')
html=html.replace(needle,needle+'\n<script src="exceljs.min.js"></script>\n<script src="v111-fixes.js"></script>',1)
index.write_text(html)
