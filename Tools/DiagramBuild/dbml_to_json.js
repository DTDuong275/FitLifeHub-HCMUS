// Đọc file DBML bằng parser chính thức @dbml/core, ghi cấu trúc đã chuẩn hóa ra JSON.
// Dùng: node dbml_to_json.js <file.dbml> <out.json>      (cần: npm install @dbml/core, hoặc đặt NODE_PATH)
const fs = require('fs');
const { Parser } = require('@dbml/core');

const src = fs.readFileSync(process.argv[2], 'utf8');
let db;
try {
  db = new Parser().parse(src, 'dbmlv2');
} catch (e) {
  const diags = (e.diags || [{ message: e.message }]).slice(0, 20);
  diags.forEach(d => console.error('LỖI CÚ PHÁP', d.message, 'dòng', d.location && d.location.start.line, 'cột', d.location && d.location.start.column));
  process.exit(1);
}
fs.writeFileSync(process.argv[3], JSON.stringify(db.normalize()));
