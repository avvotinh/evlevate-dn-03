# Financial Data Analyzer - Workshop 01

## Tổng quan

Ứng dụng CLI phân tích dữ liệu tài chính từ file CSV sử dụng OpenAI API. Hệ thống này được thiết kế để xử lý dữ liệu XBRL từ EDINET (Electronic Disclosure for Investors' NETwork) của Nhật Bản và phân tích các chỉ số tài chính quan trọng.

## Tính năng chính

- **Đọc và xử lý file CSV**: Hỗ trợ multiple encoding (UTF-8, UTF-16, Shift-JIS, EUC-JP, v.v.)
- **Phân tích dữ liệu tài chính**: Tự động trích xuất các chỉ số tài chính quan trọng
- **Tích hợp Azure OpenAI API**: Sử dụng Azure OpenAI để phân tích và đưa ra nhận định về tình hình tài chính
- **Hỗ trợ nhiều loại báo cáo**:
  - Semi-Annual Reports (mã 160)
  - Extraordinary Reports (mã 180)
  - Generic Reports (các loại khác)
- **Xuất kết quả**: Lưu kết quả phân tích vào file text với metadata đầy đủ

## Cài đặt

1. **Clone project và chuyển vào thư mục**:

```bash
cd Workshop_01
```

2. **Cài đặt dependencies**:

```bash
pip install -r requirements.txt
```

3. **Cấu hình Azure OpenAI API**:

Tạo file `.env` trong thư mục project với nội dung:

```bash
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_API_BASE=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

**Lưu ý**:

- Thay thế `your-resource-name` bằng tên Azure OpenAI resource của bạn
- Thay thế `your-api-key-here` bằng API key thực tế
- Thay thế `your-deployment-name` bằng tên deployment model (ví dụ: gpt-4, gpt-35-turbo)
- File `.env` sẽ không được commit vào git (đã thêm vào .gitignore)

## Sử dụng

### Lệnh cơ bản

```bash
python app.py --file <đường_dẫn_file_csv>
```

### Ví dụ sử dụng

```bash
# Phân tích file CSV cơ bản
python app.py --file samples/sample01.csv

# Chỉ định file output
python app.py --file samples/sample01.csv --output my_analysis.txt
```

### Tham số command line

- `-f, --file`: Đường dẫn đến file CSV cần phân tích (bắt buộc)
- `-o, --output`: Đường dẫn file output (tùy chọn, mặc định tự tạo trong thư mục outputs/)

## Dữ liệu đầu vào

File CSV cần có cấu trúc với các cột:

- `要素ID`: Element ID
- `項目名`: Item name
- `コンテキストID`: Context ID
- `相対年度`: Relative year
- `連結・個別`: Consolidated/Individual
- `期間・時点`: Period/Point in time
- `ユニットID`: Unit ID
- `単位`: Unit
- `値`: Value

## Kết quả đầu ra

Kết quả phân tích bao gồm:

1. **Thông tin công ty**: Tên, mã EDINET, loại báo cáo
2. **Chỉ số tài chính chính**:

   - Doanh thu (Revenue)
   - Lợi nhuận hoạt động (Operating Profit)
   - Lợi nhuận ròng (Net Profit)
   - Tổng tài sản (Total Assets)
   - Tổng nợ phải trả (Total Liabilities)
   - Dòng tiền từ hoạt động kinh doanh (Cash Flow)
   - Vốn chủ sở hữu (Equity)

3. **Phân tích xu hướng**:
   - Tỷ lệ tăng trưởng
   - Phân tích lợi nhuận
   - Đánh giá sức khỏe tài chính
   - Những insight quan trọng
   - Các yếu tố rủi ro

## Ví dụ output

File kết quả sẽ có dạng:

```
Financial Data Analysis Report (CSV Source)
=============================================
Source File: samples/sample01.csv
Company: [Tên công ty]
Document Type: [Loại báo cáo]
Period: [Kỳ báo cáo]
Analysis Date: 2025-01-27 10:30:45
Model Used: GPT-4o-mini
=============================================

[Nội dung phân tích chi tiết...]
```

## License

Project này được tạo cho mục đích học tập và nghiên cứu.

## Liên hệ

Nếu có thắc mắc hoặc góp ý, vui lòng tạo issue trong repository.
