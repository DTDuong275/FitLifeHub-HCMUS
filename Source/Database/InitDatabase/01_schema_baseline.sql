/* =====================================================================
   FitLife Hub - GIAI DOAN 2 - 01_schema_baseline.sql
   - Tao CSDL FitLifeHub; SET QUOTED_IDENTIFIER ON
   - Tao 22 bang theo GD1 v3 (20 bang ERD + THONG_KE_CHECKIN + DOANH_THU_NGAY), 35 khoa ngoai
   - Chi PK / FK / UNIQUE / CHECK (chua partition, chua index ho tro) de do TRUOC
   - IDENTITY cho HOI_VIEN, NHAN_VIEN, PHONG, LICH_SU_DIEU_CHUYEN, DANG_KY_GOI, CHECK_IN, LICH_HEN_PT, DANH_GIA_PT
   - UQ_LH_HLV_Gio, UQ_LH_HV_Gio (WHERE TrangThai<>'Huy') cho chong dat trung
   ===================================================================== */