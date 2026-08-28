# Tinh luong Cong doan Phat (v3 - Django, nhieu nguoi dung)

Webapp noi bo (mang LAN/VPN), phan quyen theo buu cuc, xay bang Django +
SQLite + waitress. Muc tieu cuoi cung: chinh thuc chot bang luong cho 4
cong doan (Phat, Thu Gom, Van chuyen, Khai thac). Lan nay chi lam **cong
doan Phat**; app `core` (nhan su, buu cuc, phan quyen) dung chung cho cac
cong doan sau.

Xem chi tiet thiet ke tai `C:\Users\TTVH-LeThanhBinh\.claude\plans\ancient-leaping-flask.md`.

## Trang thai hien tai (Milestone 1)

Da lam:
- Dang nhap + 3 vai tro: Admin, Phong ban, Truong buu cuc (chi thay/sua
  du lieu buu cuc minh - da kiem thu tu dong + thu cong).
- Quan ly Nhan vien/Buu cuc (Admin qua `/admin/`, Truong buu cuc qua
  `/nhan-vien/`).
- Import du lieu tho hang ngay tu file `SanLuongChiTiet_DDMMYYYY.xlsx`
  (lenh `import_daily_production`), tu dong tinh lai "tam tinh" ngay sau
  khi import.
- Bang anh xa dich vu/nhom gia (`ServiceMapping`, `RouteGroupMapping`,
  `PriceCard`) sua duoc qua `/admin/` (khong can sua code).
- Truong buu cuc tu nhap khoan ho tro (`/ho-tro/`) cho nhan vien buu cuc
  minh, tu dong cong lai vao tong thu nhap.
- Xem chi tiet theo lao dong/theo buu cuc (`/luong/<nam>/<thang>/`), xuat
  Excel, luon ghi nhan **"TAM TINH - CHUA XAC MINH"**.
- Bao cao du lieu chua anh xa duoc (`/bao-cao/chua-anh-xa/`, chi Admin) -
  dung de biet con thieu quy tac anh xa gi.

Chua lam (de sau, xem plan): quy trinh xac nhan/chot thang chinh thuc
(`PostOfficeConfirmation`), so sanh giua cac thang, canh bao bat thuong.
Cau truc du lieu cho cac phan nay da co san.

**QUAN TRONG**: bang `ServiceMapping`/`RouteGroupMapping`/`PriceCard` hien
**dang trong** (chua co du lieu that). Moi con so "cong theo san luong"
hien la 0 cho toi khi Admin cau hinh cac bang nay - xem muc "Con thieu"
ben duoi. Day la thiet ke co chu dich, tranh doan sai gia/anh xa.

## Cach chay

1. Can Python 3.10+ (khuyen nghi). Neu chua co, cai tai
   https://www.python.org/downloads/ (tick "Add python.exe to PATH").
2. Bam dup `run_app.bat` (lan dau se tu cai thu vien, can internet).
   Webapp chay tai `http://<IP may nay>:8000/` - may khac trong mang
   LAN/VPN cung truy cap duoc qua dia chi nay.
3. Dang nhap bang tai khoan admin da tao san (xem lich su thiet lap - neu
   quen mat khau, doi bang `python manage.py changepassword admin`).

### Chay thuong truc (khong can mo cua so lenh)

Tao 1 Scheduled Task chay `serve.py` moi khi khoi dong may chu:

```bash
schtasks /create /tn "TinhLuongCongDoan_Web" /tr "\"C:\Path\To\python.exe\" \"D:\ONEDRIVE\Trung tam Van hanh - BDTP Hue 05.2025\2026\San luong tinh luong cac cong doan\TinhLuongCongDoan\serve.py\"" /sc onstart /ru SYSTEM /f
```

(Thay `C:\Path\To\python.exe` bang duong dan Python that, xem bang
`where python`.)

### Tai + Import du lieu san luong hang ngay (tu dong)

`scripts/pull_and_import_daily.bat` gop 2 buoc: tai file
`SanLuongChiTiet_DDMMYYYY.xlsx` moi nhat qua WinSCP (site da luu ten
`cas_hue@10.1.45.10` - xem huong dan tao Saved Site truoc do) roi tu dong chay
`import_daily_production`. Dat lich chay moi ngay sau 10h:

```bash
schtasks /create /tn "TinhLuongCongDoan_ImportHangNgay" /tr "\"D:\ONEDRIVE\Trung tam Van hanh - BDTP Hue 05.2025\2026\San luong tinh luong cac cong doan\TinhLuongCongDoan\scripts\pull_and_import_daily.bat\"" /sc daily /st 10:15 /f
```

Log ghi vao `scripts/pull_log.txt`.

### Sao luu hang dem

```bash
schtasks /create /tn "TinhLuongCongDoan_Backup" /tr "cmd /c \"cd /d D:\ONEDRIVE\Trung tam Van hanh - BDTP Hue 05.2025\2026\San luong tinh luong cac cong doan\TinhLuongCongDoan && python manage.py backup_db\"" /sc daily /st 02:00 /f
```

Backup luu trong thu muc `backups/`, giu 30 ngay gan nhat.

## Tao tai khoan Truong buu cuc

Vao `/admin/` (dang nhap bang tai khoan Admin) → **Nguoi su dung** → Them
vao → tao username/mat khau → trong phan "Ho so nguoi dung" (Profile) o
duoi trang, chon vai tro **Truong buu cuc** + chon dung **Buu cuc phu
trach**. Tai khoan nay chi thay/sua duoc du lieu cua buu cuc do.

## Con thieu de tinh dung "cong theo san luong" (can TCHC/TCKH xac nhan)

Hien bang anh xa dang de trong co chu dich (xem canh bao o tren). Can lam
tiep khi co xac nhan:

1. **Bang anh xa dich vu** (`/admin/phat/servicemapping/`): moi to hop
   (SERVICE_CODE, TYPE_CODE_PAYROLL, SERVICE_NAME_PAYROLL, AREA_CODE,
   khoang can nang) tuong ung voi 1 trong ~49 loai dich vu chuan. Xem
   trang `/bao-cao/chua-anh-xa/` de biet chinh xac cac to hop dang xuat
   hien trong du lieu thuc te (da liet ke ~29 to hop tu file ngay
   26/08/2026, bao gom ca cac truong hop tung nghi ngo truoc day: "C-Bao
   Phat", "Goi nho thuong", "L-AppEpacket").
2. **Bang Tuyen → Nhom gia** (`/admin/phat/routegroupmapping/`): moi
   ROUTE_PO_CODE ung voi 1 Nhom don gia (1-12).
3. **Bang gia** (`/admin/phat/pricecard/`): don gia theo (loai dich vu x
   nhom gia).
4. Xac nhan lai voi TCHC/TCKH: dung "don gia chot noi bo BDTP Hue" hay
   "don gia TCT" lam co so chinh thuc (nguoi dung da chon dung don gia
   chot noi bo cho phien ban truoc - ap dung tiep cho ban nay).

Sau khi dien du 3 bang tren, chay lai `python manage.py import_daily_production`
(hoac doi lan import ke tiep) la so lieu se tu tinh dung, khong can sua
code.

## Module Khai thac (buu cuc KTC1 Hue 1, ma 530100)

Khac Phat (doc file Excel), module nay ket noi TRUC TIEP toi SQL Server
cua phan mem BCCP (2 database: `BCCP530100_2024` va `BCCP530900` cho rieng
Loai KT1 - xem `docs/01_GOVERNANCE/PROJECT_DECISIONS.md` DEC-016).

**Thiet lap mat khau SQL Server (chi lam 1 lan, tu may cua ban - KHONG ai
khac duoc go ho mat khau nay, ke ca AI):**

```powershell
$cred = Get-Credential -UserName sa
$cred.Password | ConvertFrom-SecureString | Set-Content "$env:USERPROFILE\.khaithac_sql_pw.txt"
```

File nay chi giai ma duoc tren dung may + dung user Windows da tao no
(Windows DPAPI), khong the copy sang may khac.

**Import du lieu (tung thang mot):**

```bash
python manage.py import_khaithac_production --tu 2026-07-01 --den 2026-08-01
```

**Seed lai don gia/anh xa** (chi can chay lai neu VB1054/VB1182 duoc thay
the boi 1 van ban dieu chinh moi, hoac them Nhom dich vu moi):

```bash
python manage.py seed_khaithac_pricing
```

**Import Bang phan ca thuc te** (file "BCC he so <nam> (LT).xlsx", 1
sheet/thang vd `T7.26`), can de chia Quy tien luong cho tung nhan vien
theo He so ca (VB1054 muc 1.3):

```bash
python manage.py import_khaithac_shift_roster --thang 2026-07
```

Xem ket qua tai `/khai-thac/` (Quy tien luong + luong tung nhan vien theo
ca/ngay/thang) va `/khai-thac/chua-anh-xa/` (Loai chua duoc xac dinh Nhom
dich vu - hien tai la `KT1`, can PO/TCHC xac nhan).

**QUAN TRONG - chua lam xong**: He so chat luong thang
(`KhaiThacQualityCoefficient`, VB1054 muc 1.4, Phu luc 01) hien mac dinh
1.0 (Dat) cho moi nguoi vi CHUA CO noi dung Phu luc 01 that - sua qua
`/admin/` khi PO cung cap.

## Cau truc du an

```
TinhLuongCongDoan/
  payroll/            - settings, urls goc
  core/                - Nhan vien, Buu cuc, phan quyen (dung chung 4 cong doan)
  phat/                - Module cong doan Phat
    models.py          - toan bo bang du lieu (xem plan de biet chi tiet)
    services/
      importer.py       - doc file SanLuongChiTiet_*.xlsx
      pricing.py         - anh xa dich vu + tinh tam tinh
    management/commands/
      import_daily_production.py
      seed_reference_data.py  - tao san danh muc khoan ho tro
      backup_db.py
    views.py, urls.py, forms.py, admin.py, templates/
  khaithac/            - Module cong doan Khai thac (buu cuc 530100)
    models.py          - du lieu tho theo ca/ngay, anh xa Nhom, don gia, phan ca
    services/
      sql_source.py     - ket noi SQL Server (giai ma mat khau DPAPI trong bo nho)
      pricing.py         - tinh Quy tien luong theo VB1054/1182
    management/commands/
      import_khaithac_production.py
      seed_khaithac_pricing.py
      import_khaithac_shift_roster.py
    views.py, urls.py, admin.py, templates/
  serve.py             - chay production bang waitress
  run_app.bat          - bam dup de chay thu tren Windows
  requirements.txt
```

## Kiem thu

```bash
python manage.py test
```

10 test module Phat (co che phan quyen theo buu cuc, import file mau) + 6
test module Khai thac (`compute_fund_breakdown`: don gia dung theo thoi
diem hieu luc, Loai chua anh xa bi loai khoi tong, gop dung nhieu muc can
vao 1 Loai; `compute_employee_shares`: chia dung theo He so ca, ap dung
He so chat luong, dong chua khop ten van tinh vao tong nhung khong co
nguoi nhan).
