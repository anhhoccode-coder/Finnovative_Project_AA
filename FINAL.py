import streamlit as st
import hashlib
import random
import time
import pandas as pd
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Dict, List, Any, Tuple, Optional


# 0) HỆ THỐNG DỊCH NGÔN NGỮ
st.set_page_config(
    page_title="Z-SHIELD SOC",
    layout="wide",
    initial_sidebar_state="expanded"
)

TRANS_DICT = {
    "vi": {
        # --- HEADER ---
        "title": "Z-SHIELD: NHÂN ĐIỀU HÀNH BẢO MẬT",
        "subtitle": "PHIÊN: {session} | MÃ HÓA: AES-256-GCM (Mô phỏng)",
        "btn_reboot": "KHỞI ĐỘNG LẠI HỆ THỐNG",

        # --- SIDEBAR PANEL ---
        "panel_title": "BẢNG ĐIỀU KHIỂN",
        "preset_header": "0. CẤU HÌNH NHANH (PRESET)",
        "preset_label": "CHỌN PRESET",
        "preset_note": "Preset tự cấu hình: ZKP, Cấp độ mã hóa, và bán kính GPS.",

        # --- Z-AGE ---
        "age_header": "1. Z-AGE (XÁC THỰC ĐỦ 18 TUỔI)",
        "age_desc": "Fallback: nhập tay ngày sinh.",
        "age_check": "ỨNG DỤNG YÊU CẦU XÁC THỰC 18+",
        "age_muted": "Đang tắt xác thực tuổi (một số ứng dụng không yêu cầu).",
        "age_input": "NGÀY THÁNG NĂM SINH",
        "btn_verify_age": "XÁC THỰC ĐỦ 18 TUỔI",
        "age_ok": "Đủ 18 tuổi",
        "age_fail": "Chưa đủ 18 tuổi",

        # --- Z-FACE ---
        "face_header": "2. Z-FACE VERIFIER",
        "face_desc": "Chặn ảnh camera raw, chỉ gửi bằng chứng (proof)",
        "face_check": "BẬT LỚP ZKP",
        "face_slider": "Cấp độ mã hóa",

        # --- Z-GEO ---
        "geo_header": "3. Z-GEO (LÀM NHIỄU VỊ TRÍ)",
        "geo_desc": "Che giấu toạ độ GPS chính xác",
        "geo_check": "CHE GIẤU VỊ TRÍ THỰC",
        "geo_input": "BÁN KÍNH LÀM NHIỄU (m)",

        # --- APP MANAGER ---
        "app_header": "4. QUẢN LÝ ỨNG DỤNG ĐÍCH",
        "app_select": "CHỌN ỨNG DỤNG",
        "app_status": "TRẠNG THÁI:",
        "btn_kill": "NGẮT KẾT NỐI (KILL)",

        # --- METRICS ---
        "metric_threat": "MỨC ĐE DỌA",
        "metric_log": "SỐ SỰ KIỆN LOG",
        "metric_block": "ĐÃ CHẶN NGẮT",
        "metric_latency": "ĐỘ TRỄ HỆ THỐNG",
        "sub_policy": "Theo chính sách",
        "sub_realtime": "Thời gian thực",
        "sub_action": "Theo hành động",
        "sub_stable": "Ổn định",

        # --- TABS ---
        "tab_1": "GIÁM SÁT TRỰC TIẾP",
        "tab_2": "GÓC NHÌN CỦA ỨNG DỤNG",
        "monitor_layer": "CÁC LỚP BẢO VỆ ĐANG HOẠT ĐỘNG",
        "src_cam": "NGUỒN ĐẦU VÀO: CAMERA 01",
        "cam_label": "CHỤP ẢNH KHUÔN MẶT (TỪ CAMERA)",
        "data_out": "DỮ LIỆU XUẤT (GỬI TỚI ỨNG DỤNG)",

        # --- DYNAMIC DATA KEYS ---
        "lbl_mode": "Chế độ",
        "lbl_sec": "Bảo mật",
        "lbl_priv": "Riêng tư",
        "lbl_data": "Dữ liệu",
        "lbl_proof": "Mã Proof",
        "lbl_chain": "Neo chuỗi",
        "lbl_warn": "Cảnh báo",

        "val_zkp": "CHỈ GỬI BẰNG CHỨNG (ZKP)",
        "val_raw": "ẢNH GỐC (RAW)",
        "val_risk": "NGUY CƠ RÒ RỈ CAO",
        "val_sec_max": "RẤT CAO",
        "val_sec_high": "CAO",
        "val_sec_basic": "CƠ BẢN",
        "val_sec_med": "TRUNG BÌNH",
        "val_sec_low": "THẤP",
        "val_priv_max": "ẨN DANH TUYỆT ĐỐI",
        "val_priv_high": "BẢO VỆ MẠNH",
        "val_priv_opt": "TỐI ỨU",
        "val_priv_med": "TRUNG BÌNH",

        # --- ACTIONS ---
        "btn_gen_proof": "TẠO VÀ GHI LOG PROOF",
        "msg_proof_ok": "Đã tạo proof và ghi log (không lưu ảnh raw).",
        "btn_ver_proof": "XÁC THỰC PROOF MỚI NHẤT",
        "msg_ver_ok": "Xác thực thành công. Cho phép truy cập",
        "msg_ver_fail": "Xác thực thất bại.",
        "warn_no_proof": "Chưa có proof. Hãy tạo proof trước.",

        "warn_raw": "[Nguy hiểm!] Dữ liệu có nguy cơ rò rỉ cao",
        "ask_raw": "Bạn có chắc muốn gửi dữ liệu xác thực khuôn mặt đến {app}?",
        "btn_raw_open": "GỬI ẢNH RAW (CẢNH BÁO)",
        "check_raw": "Tôi hiểu rủi ro và vẫn muốn gửi dữ liệu",
        "btn_raw_send": "XÁC NHẬN GỬI RAW",
        "msg_raw_sent": "Đã gửi ảnh raw (mô phỏng). Nguy cơ rò rỉ cao.",
        "msg_raw_deny": "Bạn cần tick xác nhận rủi ro trước khi gửi.",
        "val_threat_low": "THẤP",
        "val_threat_high": "CAO",
        "val_threat_med": "TRUNG BÌNH",
        "val_sec_max": "RẤT CAO",
        "lbl_age_num": "Tuổi",
        "log_stt_success": "THÀNH CÔNG",
        "log_stt_danger": "NGUY HIỂM",
        "log_stt_term": "ĐÃ NGẮT",
        "log_desc_reboot": "Hệ thống khởi động lại",
        "log_act_sys": "HỆ THỐNG",
        "fmt_proof_created": "Đã tạo Proof {id}",
        "fmt_verified": "Đã xác thực {id}",
        "fmt_raw_sent": "Gửi ảnh RAW {size} KB",
        "fmt_check_age": "Kiểm tra tuổi: {age}",
        "fmt_spoof": "Làm nhiễu bán kính {radius}m",
        "fmt_force_kill": "Ngắt cưỡng bức {app}",
        # --- GPS ---
        "gps_header": "GIÁM SÁT GPS",
        "gps_real": "CẢM BIẾN THẬT (THIẾT BỊ)",
        "gps_fake": "CẢM BIẾN ẢO (ĐÃ LÀM NHIỄU - {radius}m)",
        "addr_real": "Địa chỉ hiện tại:",
        "gps_risk": "[Nguy hiểm!] GPS thật đang lộ (không làm nhiễu).",
        "gps_safe": "Khu vực sau làm nhiễu:",
        "btn_update_gps": "CẬP NHẬT TOẠ ĐỘ",

        "addr_full": "Linh Trung, Thủ Đức, TP HCM (Mô phỏng)",
        "addr_obfuscated": "Bán kính {r}m quanh Thủ Đức, TP HCM (Đã làm nhiễu)",

        # --- ANALYSIS ---
        "analysis_header": "PHÂN TÍCH BẢO MẬT (MVP)",
        "log_empty": "Chưa có log. Hãy tạo proof / cập nhật GPS / ngắt kết nối để tạo dữ liệu phân tích.",

        # --- APP VIEW ---
        "app_disconnect": "KẾT NỐI ĐẾN {app} ĐÃ BỊ NGẮT.",
        "app_view_title": "GÓC NHÌN ỨNG DỤNG: {app}",
        "app_view_desc": "Trạng thái hiển thị theo dữ liệu xác thực bạn đã thực hiện ở Tab 'Giám sát trực tiếp'.",

        # --- FOOTER ---
        "log_header": "NHẬT KÝ KIỂM TOÁN BẢO MẬT",
        "log_safe": "Chưa phát hiện bất thường.",
        "btn_download": "TẢI NHẬT KÝ (CSV)",

        # --- OPTIONS ---
        "opt_strict": "NGHIÊM NGẶT (Ngân hàng/KYC)",
        "opt_balance": "CÂN BẰNG (Mạng xã hội)",
        "opt_dev": "CHẾ ĐỘ DEV",

        # --- ENCRYPTION DEPTH ---
        "depth_low": "Trung bình",
        "depth_opt": "Tối ưu",
        "depth_high": "Nâng cao",
        "depth_max": "Tối đa",

        # --- STATUS TEXT ---
        "status_on": "BẬT",
        "status_off": "TẮT",
        "status_ok": "ĐẠT",
        "status_missing": "THIẾU",
        "status_na": "KHÔNG CÓ",
        "status_con": "ĐÃ KẾT NỐI",
        "status_term": "ĐÃ NGẮT KẾT NỐI",

        # --- OTHER KEYS ---
        "val_blob": "Khối Proof {b} bytes",
        "note_zkp": "Lớp ZKP đang bật",
        "app_view_line1": "{name} đã được Z Shield xác thực sinh trắc học thành công.",
        "app_view_line1_fail": "Chưa có xác thực sinh trắc học (hãy tạo proof).",
        "app_view_line2_ok": "Đã xác thực đủ 18 tuổi.",
        "app_view_line2_fail": "Chưa xác thực đủ 18 tuổi (nhập ngày sinh ở Z Age).",
        "app_view_line2_off": "Ứng dụng không yêu cầu xác thực 18+ (đang tắt).",
        "app_view_line3": "Xác thực giấy tờ: Không sử dụng (fallback nhập tay).",

        # --- LOG ANALYSIS ---
        "chart1_title": "Biểu đồ 1: Số sự kiện theo phút",
        "chart2_title": "Biểu đồ 2: Phân bố trạng thái",
        "chart3_title": "Biểu đồ 3: Hành động phổ biến",
        "layer_info": "Lớp bảo vệ: {layers}",
    },
    "en": {
        # --- HEADER ---
        "title": "Z-SHIELD: SECURITY OPS CENTER",
        "subtitle": "SESSION: {session} | ENCRYPTION: AES-256-GCM (Simulated)",
        "btn_reboot": "REBOOT SYSTEM",

        # --- SIDEBAR PANEL ---
        "panel_title": "CONTROL PANEL",
        "preset_header": "0. QUICK CONFIG (PRESET)",
        "preset_label": "SELECT PRESET",
        "preset_note": "Auto-config: ZKP, Encryption Level, and GPS Radius.",

        # --- Z-AGE ---
        "age_header": "1. Z-AGE (AGE VERIFICATION 18+)",
        "age_desc": "Fallback: Manual date of birth entry.",
        "age_check": "APP REQUIRES 18+ VERIFICATION",
        "age_muted": "Age verification is OFF (not required by some apps).",
        "age_input": "DATE OF BIRTH",
        "btn_verify_age": "VERIFY 18+ STATUS",
        "age_ok": "Valid 18+",
        "age_fail": "Under 18",

        # --- Z-FACE ---
        "face_header": "2. Z-FACE VERIFIER",
        "face_desc": "Block raw camera, send Zero-Knowledge Proof only",
        "face_check": "ENABLE ZKP LAYER",
        "face_slider": "Encryption Level",

        # --- Z-GEO ---
        "geo_header": "3. Z-GEO (LOCATION OBFUSCATION)",
        "geo_desc": "Mask exact GPS coordinates",
        "geo_check": "MASK REAL LOCATION",
        "geo_input": "SPOOFING RADIUS (m)",

        # --- APP MANAGER ---
        "app_header": "4. TARGET APP MANAGEMENT",
        "app_select": "SELECT APP",
        "app_status": "STATUS:",
        "btn_kill": "TERMINATE CONNECTION (KILL)",

        # --- METRICS ---
        "metric_threat": "THREAT LEVEL",
        "metric_log": "LOG EVENTS",
        "metric_block": "BLOCKED ACTIONS",
        "metric_latency": "SYSTEM LATENCY",
        "sub_policy": "Policy-based",
        "sub_realtime": "Real-time",
        "sub_action": "Action-based",
        "sub_stable": "Stable",

        # --- TABS ---
        "tab_1": "LIVE MONITORING",
        "tab_2": "APPLICATION VIEW",
        "monitor_layer": "ACTIVE PROTECTION LAYERS",
        "src_cam": "INPUT SOURCE: CAMERA 01",
        "cam_label": "CAPTURE FACE (FROM CAMERA)",
        "data_out": "OUTPUT DATA (SENT TO APP)",

        # --- DYNAMIC DATA KEYS ---
        "lbl_mode": "Mode",
        "lbl_sec": "Security",
        "lbl_priv": "Privacy",
        "lbl_data": "Data Payload",
        "lbl_proof": "Proof ID",
        "lbl_chain": "On-Chain Tx",
        "lbl_warn": "Warning",

        "val_zkp": "ZKP PROOF ONLY",
        "val_raw": "RAW IMAGE",
        "val_risk": "HIGH RISK DATA LEAK",
        "val_sec_max": "MAXIMUM",
        "val_sec_high": "HIGH",
        "val_sec_basic": "BASIC",
        "val_sec_med": "MEDIUM",
        "val_sec_low": "LOW",
        "val_priv_max": "MAX ANONYMITY",
        "val_priv_high": "STRONG PRIVACY",
        "val_priv_opt": "OPTIMAL",
        "val_priv_med": "MEDIUM",
        "log_stt_success": "SUCCESS",
        "log_stt_danger": "DANGER",
        "log_stt_term": "TERMINATED",
        "log_desc_reboot": "System Rebooted",
        "log_act_sys": "SYSTEM",
        # --- ACTIONS ---
        "btn_gen_proof": "GENERATE & LOG PROOF",
        "msg_proof_ok": "Proof generated & logged (Raw image discarded).",
        "btn_ver_proof": "VERIFY LATEST PROOF",
        "msg_ver_ok": "Verification Successful. Access Granted.",
        "msg_ver_fail": "Verification Failed.",
        "warn_no_proof": "No proof found. Please generate one first.",

        "warn_raw": "[DANGER!] High risk of data leakage",
        "ask_raw": "Are you sure you want to send RAW face data to {app}?",
        "btn_raw_open": "SEND RAW PHOTO (WARNING)",
        "check_raw": "I understand the risk and want to proceed",
        "btn_raw_send": "CONFIRM SEND RAW",
        "msg_raw_sent": "Raw photo sent (Simulated). High leakage risk.",
        "msg_raw_deny": "You must check the confirmation box.",
        "val_risk": "HIGH RISK DATA LEAK",
        "val_threat_low": "LOW",
        "val_threat_high": "HIGH",
        "val_threat_med": "MEDIUM",
        "lbl_age_num": "Age",
        "val_sec_max": "MAXIMUM",
        "fmt_proof_created": "Proof {id} created",
        "fmt_verified": "Verified {id}",
        "fmt_raw_sent": "Sent RAW {size} KB",
        "fmt_check_age": "Check Age: {age}",
        "fmt_spoof": "Spoofed radius {radius}m",
        "fmt_force_kill": "Force terminated {app}",
        # --- GPS ---
        "gps_header": "GPS MONITORING",
        "gps_real": "REAL SENSOR (DEVICE)",
        "gps_fake": "VIRTUAL SENSOR (SPOOFED - {radius}m)",
        "addr_real": "Current Address:",
        "gps_risk": "[DANGER!] Real GPS exposed (No spoofing).",
        "gps_safe": "Spoofed Area:",
        "btn_update_gps": "UPDATE COORDINATES",

        "addr_full": "Linh Trung, Thu Duc, HCMC (Simulated)",
        "addr_obfuscated": "Radius {r}m around Thu Duc, HCMC (Obfuscated)",

        # --- ANALYSIS ---
        "analysis_header": "SECURITY ANALYSIS (MVP)",
        "log_empty": "No logs yet. Generate proof / update GPS / kill connection to generate data.",

        # --- APP VIEW ---
        "app_disconnect": "CONNECTION TO {app} TERMINATED.",
        "app_view_title": "APPLICATION VIEW: {app}",
        "app_view_desc": "State displayed based on authentication data from 'Live Monitoring' tab.",

        # --- FOOTER ---
        "log_header": "SECURITY AUDIT LOG",
        "log_safe": "No anomalies detected.",
        "btn_download": "DOWNLOAD LOGS (CSV)",

        # --- OPTIONS ---
        "opt_strict": "STRICT (Banking/KYC)",
        "opt_balance": "BALANCED (Social Media)",
        "opt_dev": "DEV MODE",

        # --- ENCRYPTION DEPTH ---
        "depth_low": "Medium",
        "depth_opt": "Optimal",
        "depth_high": "High",
        "depth_max": "Maximum",

        # --- STATUS TEXT ---
        "status_on": "ON",
        "status_off": "OFF",
        "status_ok": "OK",
        "status_missing": "MISSING",
        "status_na": "N/A",
        "status_con": "CONNECTED",
        "status_term": "TERMINATED",

        # --- OTHER KEYS ---
        "val_blob": "Proof Blob {b} bytes",
        "note_zkp": "ZKP Active",
        "app_view_line1": "{name} has been successfully verified by Z Shield biometric authentication.",
        "app_view_line1_fail": "No biometric verification (please generate proof).",
        "app_view_line2_ok": "Age 18+ verified.",
        "app_view_line2_fail": "Age 18+ not verified (enter birth date in Z Age).",
        "app_view_line2_off": "App does not require 18+ verification (disabled).",
        "app_view_line3": "ID Document: Not used (fallback manual entry).",

        # --- LOG ANALYSIS ---
        "chart1_title": "Chart 1: Events per minute",
        "chart2_title": "Chart 2: Status distribution",
        "chart3_title": "Chart 3: Common actions",
        "layer_info": "Protection layers: {layers}",
    }
}


def init_language():
    if 'language' not in st.session_state:
        st.session_state.language = 'vi'


def t(key, **kwargs):
    """Translation function"""
    init_language()
    lang = st.session_state.language
    text_template = TRANS_DICT.get(lang, TRANS_DICT["vi"]).get(key, key)
    if kwargs:
        return text_template.format(**kwargs)
    return text_template

# 1) CSS STYLE & FRONTEND
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #0e1117;
    color: #E5E7EB;
}
.stMetric {
    background-color: #1f2937;
    padding: 15px;
    border-radius: 6px;
    border-left: 5px solid #00ff41;
}
.stButton > button {
    width: 100%;
    border-radius: 0px;
    font-weight: 700;
    text-transform: uppercase;
    border: 1px solid #4b5563;
    background-color: #111827;
    color: #00ff41;
}
.stButton > button:hover {
    background-color: #00ff41;
    color: #000000;
    border-color: #00ff41;
}
h1, h2, h3 {
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #374151;
}
.small-muted {
    color: #9ca3af;
    font-size: 12px;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border: 1px solid #374151;
    margin-right: 8px;
    font-size: 12px;
}
.badge-ok { color: #00ff41; }
.badge-warn { color: #f59e0b; }
.badge-danger { color: #ef4444; }
.white-app-view {
    background: #ffffff;
    color: #111827;
    border-radius: 10px;
    padding: 40px;
    min-height: 520px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.white-app-card {
    text-align: center;
    max-width: 720px;
}
.big-check {
    width: 84px;
    height: 84px;
    border-radius: 999px;
    background: #16a34a;
    color: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 44px;
    margin-bottom: 18px;
}
.app-lines {
    font-size: 24px;
    line-height: 1.6;
}
.app-sub {
    margin-top: 10px;
    font-size: 16px;
    color: #374151;
}
</style>
""",
    unsafe_allow_html=True,
)



# 2) MÔ HÌNH DỮ LIỆU (DATA MODELS)

@dataclass
class ProofPackage:
    proof_id: str
    algorithm: str
    curve: str
    payload_size: float
    original_size: float
    compute_time: float
    claim_type: str
    issued_at: str
    expires_at: str
    app_id: str
    tx_hash: str


@dataclass
class AuditEvent:
    ThoiGian: str
    HanhDong: str
    ChiTiet: str
    TrangThai: str
    UngDung: str


# 3) CÁC DỊCH VỤ BACKEND (SERVICES)
class AuditLogger:
    def __init__(self, state_key: str = "logs"):
        self.state_key = state_key

    @staticmethod
    def _depunct(text: str) -> str:
        return (text or "").replace("_", " ").strip()

    @staticmethod
    def _normalize_status(status: str) -> str:
        s = (status or "").strip().replace("_", " ")
        up = s.upper()
        if up in ["THÀNH CÔNG", "THANH CONG", "SUCCESS"]: return "SUCCESS"
        if up in ["NGUY HIỂM", "DANGER", "CẢNH BÁO", "HIGH RISK"]: return "DANGER"
        if up in ["ĐÃ NGẮT", "TERMINATED", "BỊ NGẮT"]: return "TERMINATED"
        return s

    def add(self, action: str, detail: str, status: str, app: str):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event = AuditEvent(
            ThoiGian=ts,
            HanhDong=self._depunct(action),
            ChiTiet=self._depunct(detail),
            TrangThai=self._normalize_status(status),
            UngDung=self._depunct(app),
        )
        st.session_state[self.state_key].insert(0, asdict(event))


class IdentityProofService:
    def __init__(self, session_salt: str):
        self.session_salt = session_salt

    def _mock_tx_hash(self, proof_id: str) -> str:
        return "0x" + hashlib.sha256((proof_id + self.session_salt).encode()).hexdigest()[:64]

    @staticmethod
    def _depth_profile_keys(encryption_depth_idx: int) -> Dict[str, str]:
        """Get profile based on encryption depth index"""
        # Index: 0=Medium, 1=Optimal, 2=High, 3=Maximum
        if encryption_depth_idx == 3:
            return {"bytes": 512, "lvl_key": "val_sec_max", "mode_key": "val_priv_max"}
        elif encryption_depth_idx == 2:
            return {"bytes": 384, "lvl_key": "val_sec_high", "mode_key": "val_priv_high"}
        elif encryption_depth_idx == 1:
            return {"bytes": 320, "lvl_key": "val_sec_basic", "mode_key": "val_priv_opt"}
        else:  # 0
            return {"bytes": 256, "lvl_key": "val_sec_med", "mode_key": "val_priv_med"}

    def generate(self, data_size_kb: float, app_id: str) -> ProofPackage:
        now = datetime.now()
        issued = now.strftime("%Y-%m-%d %H:%M:%S")
        expires = (now.replace(microsecond=0)).strftime("%Y-%m-%d %H:%M:%S")
        seed = f"{time.time()}|{random.random()}|{self.session_salt}|{app_id}"
        proof_hash = hashlib.sha3_512(seed.encode()).hexdigest()
        proof_id = proof_hash[:16]
        compute_time = random.uniform(0.02, 0.08)
        tx_hash = self._mock_tx_hash(proof_id)

        return ProofPackage(
            proof_id=proof_id,
            algorithm="Groth16 (Sim)",
            curve="bn254 (Sim)",
            payload_size=256.0,
            original_size=float(data_size_kb),
            compute_time=float(compute_time),
            claim_type="FaceID Claim",
            issued_at=issued,
            expires_at=expires,
            app_id=app_id,
            tx_hash=tx_hash,
        )

    def verify(self, proof: ProofPackage) -> bool:
        if not proof.proof_id or len(proof.proof_id) < 8: return False
        expected = "0x" + hashlib.sha256((proof.proof_id + self.session_salt).encode()).hexdigest()[:64]
        return proof.tx_hash == expected

    def app_view_payload(
            self,
            zkp_active: bool,
            encryption_depth_idx: int,
            app_id: str,
            latest_proof: Optional[Dict[str, Any]],
            original_kb: Optional[float] = None
    ) -> Dict[str, str]:
        # Get profile keys
        prof = self._depth_profile_keys(encryption_depth_idx)

        if not zkp_active:
            return {
                t("lbl_mode"): t("val_raw"),
                t("lbl_warn"): t("val_risk"),
                t("lbl_sec"): t("val_sec_low"),
                t("lbl_data"): f"Raw Face ({original_kb:.1f} KB)" if original_kb else "Raw Image",
            }

        if latest_proof:
            pid = latest_proof.get("proof_id", "N/A")
            tx = latest_proof.get("tx_hash", "N/A")
        else:
            pid = hashlib.sha256((app_id + self.session_salt).encode()).hexdigest()[:16]
            tx = "0x" + hashlib.sha256((pid + self.session_salt).encode()).hexdigest()[:64]

        return {
            t("lbl_mode"): t("val_zkp"),
            t("lbl_sec"): t(prof["lvl_key"]),
            t("lbl_priv"): t(prof["mode_key"]),
            t("lbl_data"): t("val_blob", b=prof['bytes']),
            t("lbl_proof"): pid,
            t("lbl_chain"): tx,
        }


class LocationObfuscationService:
    @staticmethod
    def spoof(lat: float, lon: float, radius_m: int) -> Tuple[float, float]:
        if radius_m <= 0: return lat, lon
        offset = radius_m / 111_320
        fake_lat = lat + (random.uniform(-1, 1) * offset)
        fake_lon = lon + (random.uniform(-1, 1) * offset)
        return fake_lat, fake_lon


class PolicyEngine:
    def evaluate(self, app_status: str, zkp_active: bool, spoof_radius: int) -> Dict[str, Any]:
        decision = {
            "allow_connection": app_status != "TERMINATED",
            "risk_level": "LOW",
            "risk_notes": [],
        }

        if app_status == "TERMINATED":
            decision["risk_level"] = "LOW"
            decision["risk_notes"].append("Kill switch active")
            return decision

        if zkp_active:
            decision["risk_notes"].append(t("note_zkp"))
        else:
            decision["risk_level"] = "HIGH"
            decision["risk_notes"].append("RISK: Raw data")

        if spoof_radius == 0:
            decision["risk_level"] = "HIGH"
            decision["risk_notes"].append("RISK: Real GPS")

        return decision


class AppRegistry:
    def __init__(self, apps: Dict[str, Dict[str, Any]]):
        self.apps = apps

    def list_apps(self) -> List[str]: return list(self.apps.keys())

    def status(self, app: str) -> str: return self.apps[app]["status"]

    def set_status(self, app: str, status: str): self.apps[app]["status"] = status


# 4) KHỞI TạO SESSION STATE (STATE MANAGEMENT)
def _new_session_id() -> str:
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]


def init_state():
    if "user_name" not in st.session_state:
        st.session_state.user_name = "User"

    if "session_id" not in st.session_state:
        st.session_state.session_id = _new_session_id()
    if "active_apps" not in st.session_state:
        st.session_state.active_apps = {
            "Shopee Mobile": {"status": "CONNECTED"},
            "Facebook Service": {"status": "CONNECTED"},
            "Ngân hàng KYC": {"status": "CONNECTED"},
        }
    if "logs" not in st.session_state: st.session_state.logs = []

    if "policy_preset_idx" not in st.session_state:
        st.session_state.policy_preset_idx = 1  # 1 = Balanced

    if "zkp_active" not in st.session_state: st.session_state.zkp_active = True
    if "encryption_depth" not in st.session_state: st.session_state.encryption_depth = 2  # Index 2 = High
    if "geo_active" not in st.session_state: st.session_state.geo_active = True
    if "spoof_radius" not in st.session_state: st.session_state.spoof_radius = 1500
    if "target_app" not in st.session_state: st.session_state.target_app = "Shopee Mobile"
    if "telemetry" not in st.session_state:
        st.session_state.telemetry = {
            "real_lat": 10.762622, "real_lon": 106.660172,
            "fake_lat": 10.762622, "fake_lon": 106.660172,
            "last_update": datetime.now().strftime("%H:%M:%S"),
        }
    if "latest_proof" not in st.session_state: st.session_state.latest_proof = None
    if "raw_confirm_mode" not in st.session_state: st.session_state.raw_confirm_mode = False
    if "raw_user_confirmed" not in st.session_state: st.session_state.raw_user_confirmed = False
    if "z_age_required" not in st.session_state: st.session_state.z_age_required = False
    if "z_age_dob" not in st.session_state: st.session_state.z_age_dob = date(2005, 1, 1)
    if "age_verified" not in st.session_state: st.session_state.age_verified = False
    if "age_payload" not in st.session_state: st.session_state.age_payload = None


init_state()

logger = AuditLogger()
registry = AppRegistry(st.session_state.active_apps)
policy_engine = PolicyEngine()
proof_service = IdentityProofService(session_salt=st.session_state.session_id)


# 5) CALLBACKS & ACTIONS
def apply_preset(idx: int):
    # 0=Strict, 1=Balance, 2=Dev
    if idx == 0:
        st.session_state.zkp_active = True
        st.session_state.encryption_depth = 3  # Maximum
        st.session_state.geo_active = True
        st.session_state.spoof_radius = 2500
    elif idx == 1:
        st.session_state.zkp_active = True
        st.session_state.encryption_depth = 1  # Optimal
        st.session_state.geo_active = True
        st.session_state.spoof_radius = 1500
    else:
        st.session_state.zkp_active = False
        st.session_state.encryption_depth = 0  # Medium
        st.session_state.geo_active = False
        st.session_state.spoof_radius = 0


def kill_connection():
    app = st.session_state.target_app
    registry.set_status(app, "TERMINATED")
    logger.add("KILL SWITCH", f"Force terminated {app}", "TERMINATED", app)


def reboot_system():
    st.session_state.logs = []
    for app in registry.list_apps():
        st.session_state.active_apps[app]["status"] = "CONNECTED"
    st.session_state.latest_proof = None
    st.session_state.raw_confirm_mode = False
    st.session_state.raw_user_confirmed = False
    st.session_state.z_age_required = False
    st.session_state.age_verified = False
    st.session_state.age_payload = None
    logger.add("SYSTEM", "System Rebooted", "SUCCESS", "SYSTEM")


def update_coordinates():
    real_lat = st.session_state.telemetry["real_lat"]
    real_lon = st.session_state.telemetry["real_lon"]
    radius = int(st.session_state.spoof_radius) if st.session_state.geo_active else 0
    f_lat, f_lon = LocationObfuscationService.spoof(real_lat, real_lon, radius)
    st.session_state.telemetry["fake_lat"] = f_lat
    st.session_state.telemetry["fake_lon"] = f_lon
    logger.add("Z GEO", f"Spoofed radius {radius}m", "SUCCESS", st.session_state.target_app)


def _calc_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# 6) HEADER & LANGUAGE CONTROL
init_language()

col_head_1, col_head_2 = st.columns([3, 1])
with col_head_1:
    st.title(t("title"))
    st.caption(t("subtitle", session=st.session_state.session_id))

with col_head_2:
    c_lang, c_btn = st.columns([1, 2])
    with c_lang:
        choice = st.selectbox(
            "🌐",
            ["VN Tiếng Việt", "EN English"],
            index=0 if st.session_state.language == 'vi' else 1,
            label_visibility="collapsed"
        )
        new_lang = "vi" if "Việt" in choice else "en"
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.rerun()

    with c_btn:
        st.button(t("btn_reboot"), on_click=reboot_system)

st.markdown("---")

# 7) MAIN LAYOUT
col_ctrl, col_main = st.columns([1, 3])

with col_ctrl:
    st.subheader(t("panel_title"))

    # PANEL: PRESET
    with st.container(border=True):
        st.markdown(f"**{t('preset_header')}**")
        preset_list = [t("opt_strict"), t("opt_balance"), t("opt_dev")]
        curr_idx = st.session_state.policy_preset_idx
        selected_str = st.selectbox(t("preset_label"), preset_list, index=curr_idx)
        new_idx = preset_list.index(selected_str)
        if new_idx != st.session_state.policy_preset_idx:
            st.session_state.policy_preset_idx = new_idx
            apply_preset(new_idx)
            logger.add("POLICY", f"Preset applied: {preset_list[new_idx]}", "SUCCESS", st.session_state.target_app)
        st.markdown(f"<span class='small-muted'>{t('preset_note')}</span>", unsafe_allow_html=True)

    # PANEL: Z-AGE
    with st.container(border=True):
        st.markdown(f"**{t('age_header')}**")
        st.caption(t("age_desc"))
        st.checkbox(t("age_check"), key="z_age_required")

        if not st.session_state.z_age_required:
            st.session_state.age_verified = False
            st.session_state.age_payload = None
            st.markdown(f"<span class='small-muted'>{t('age_muted')}</span>", unsafe_allow_html=True)
        else:
            st.session_state.z_age_dob = st.date_input(
                t("age_input"),
                value=st.session_state.z_age_dob,
                min_value=date(1900, 1, 1),
                max_value=date.today(),
            )

            if st.button(t("btn_verify_age")):
                age = _calc_age(st.session_state.z_age_dob)
                ok18 = age >= 18
                st.session_state.age_verified = bool(ok18)
                st.session_state.age_payload = {"Age": age, "Is18": ok18}
                status_log = "SUCCESS" if ok18 else "FAIL"
                logger.add("Z AGE", f"Check Age: {age}", status_log, "Z SHIELD")

            if st.session_state.age_payload:
                ap = st.session_state.age_payload
                lbl_age = t('lbl_age_num')

                if ap.get("Is18"):
                    st.success(f"{t('age_ok')} | {lbl_age}: {ap.get('Age')}")
                else:
                    st.error(f"{t('age_fail')} | {lbl_age}: {ap.get('Age')}")

    # PANEL: Z-FACE
    with st.container(border=True):
        st.markdown(f"**{t('face_header')}**")
        st.caption(t("face_desc"))
        st.checkbox(t("face_check"), key="zkp_active")

        depth_options = [t("depth_low"), t("depth_opt"), t("depth_high"), t("depth_max")]
        st.select_slider(
            t("face_slider"),
            options=depth_options,
            value=depth_options[st.session_state.encryption_depth],
            key="encryption_depth_slider"
        )
        st.session_state.encryption_depth = depth_options.index(st.session_state.encryption_depth_slider)

    # PANEL: Z-GEO
    with st.container(border=True):
        st.markdown(f"**{t('geo_header')}**")
        st.caption(t("geo_desc"))
        st.checkbox(t("geo_check"), key="geo_active")
        st.number_input(
            t("geo_input"),
            min_value=0, max_value=50000, step=50,
            key="spoof_radius",
            disabled=(not st.session_state.geo_active),
        )

    # PANEL: APP MANAGER
    with st.container(border=True):
        st.markdown(f"**{t('app_header')}**")
        st.selectbox(t("app_select"), registry.list_apps(), key="target_app")
        current_status = registry.status(st.session_state.target_app)
        st.text(f"{t('app_status')} {current_status}")
        st.button(t("btn_kill"), type="primary", on_click=kill_connection)

with col_main:
    radius_effective = int(st.session_state.spoof_radius) if st.session_state.geo_active else 0
    decision = policy_engine.evaluate(
        app_status=registry.status(st.session_state.target_app),
        zkp_active=st.session_state.zkp_active,
        spoof_radius=radius_effective,
    )

    m1, m2, m3, m4 = st.columns(4)
    raw_threat = decision["risk_level"]
    if raw_threat == "LOW":
        display_threat = t("val_threat_low")
    elif raw_threat == "HIGH":
        display_threat = t("val_threat_high")
    else:
        display_threat = t("val_threat_med")
    # -----------------------------

    blocked_count = sum(1 for x in st.session_state.logs if x.get("TrangThai") in ["TERMINATED", "DANGER"])
    latency_ms = random.randint(8, 18)

    m1.metric(t("metric_threat"), display_threat, t("sub_policy"))
    m2.metric(t("metric_log"), len(st.session_state.logs), t("sub_realtime"))
    m3.metric(t("metric_block"), blocked_count, t("sub_action"))
    m4.metric(t("metric_latency"), f"{latency_ms}ms", t("sub_stable"))

    badge_col1, badge_col2 = st.columns([2, 3])
    with badge_col1:
        zkp_status = t("status_on") if st.session_state.zkp_active else t("status_off")
        geo_status = t("status_on") if st.session_state.geo_active else t("status_off")
        st.markdown(
            f"""
            <span class="badge badge-ok">ZKP: {zkp_status}</span>
            <span class="badge badge-warn">Z GEO: {geo_status}</span>
            <span class="badge badge-warn">GPS: {radius_effective}m</span>
            <span class="badge badge-ok">APP: {st.session_state.target_app}</span>
            """,
            unsafe_allow_html=True,
        )
    with badge_col2:
        if decision["risk_notes"]:
            st.info(" | ".join(decision["risk_notes"]))

    st.markdown("---")

    tab1, tab2 = st.tabs([t("tab_1"), t("tab_2")])

    # TAB 1: MONITOR
    with tab1:
        st.subheader(t("monitor_layer"))

        c1, c2 = st.columns(2)
        with c1:
            st.info(t("src_cam"))
            cam_file = st.camera_input(t("cam_label"))
            source_file = cam_file

        with c2:
            st.warning(t("data_out"))
            if source_file:
                file_size_kb = source_file.size / 1024.0
                app_name = st.session_state.target_app

                app_payload = proof_service.app_view_payload(
                    zkp_active=st.session_state.zkp_active,
                    encryption_depth_idx=st.session_state.encryption_depth,
                    app_id=app_name,
                    latest_proof=st.session_state.latest_proof,
                    original_kb=file_size_kb
                )

                yaml_lines = [f"{k}: {v}" for k, v in app_payload.items()]
                st.code("\n".join(yaml_lines), language="yaml")

                if st.session_state.zkp_active:
                    proof = proof_service.generate(file_size_kb, app_name)
                    colv1, colv2 = st.columns(2)
                    with colv1:
                        if st.button(t("btn_gen_proof")):
                            st.session_state.latest_proof = asdict(proof)
                            logger.add("Z FACE", f"Proof {proof.proof_id} created", "SUCCESS", app_name)
                            st.success(t("msg_proof_ok"))
                    with colv2:
                        if st.button(t("btn_ver_proof")):
                            if st.session_state.latest_proof:
                                p = ProofPackage(**st.session_state.latest_proof)
                                ok = proof_service.verify(p)
                                if ok:
                                    logger.add("Z FACE", f"Verified {p.proof_id}", "SUCCESS", p.app_id)
                                    st.success(t("msg_ver_ok"))
                                else:
                                    logger.add("Z FACE", "Verify Failed", "DANGER", app_name)
                                    st.error(t("msg_ver_fail"))
                            else:
                                st.warning(t("warn_no_proof"))
                else:
                    st.error(t("warn_raw"))
                    st.warning(t("ask_raw", app=app_name))
                    if st.button(t("btn_raw_open")):
                        st.session_state.raw_confirm_mode = True
                        st.session_state.raw_user_confirmed = False

                    if st.session_state.raw_confirm_mode:
                        st.checkbox(t("check_raw"), key="raw_user_confirmed")
                        if st.button(t("btn_raw_send")):
                            if st.session_state.raw_user_confirmed:
                                logger.add("Z FACE", f"Sent RAW {file_size_kb:.1f} KB", "DANGER", app_name)
                                st.error(t("msg_raw_sent"))
                                st.session_state.raw_confirm_mode = False
                                st.session_state.raw_user_confirmed = False
                            else:
                                st.warning(t("msg_raw_deny"))

        st.divider()

        # GPS SECTION
        st.subheader(t("gps_header"))
        real_lat = st.session_state.telemetry["real_lat"]
        real_lon = st.session_state.telemetry["real_lon"]

        f_lat, f_lon = LocationObfuscationService.spoof(real_lat, real_lon, radius_effective)
        st.session_state.telemetry["fake_lat"] = f_lat
        st.session_state.telemetry["fake_lon"] = f_lon

        g1, g2 = st.columns(2)
        with g1:
            st.text(t("gps_real"))
            st.code(f"Lat: {real_lat:.6f}\nLon: {real_lon:.6f}", language="json")
            st.success(f"{t('addr_real')} {t('addr_full')}")
        with g2:
            st.text(t("gps_fake", radius=radius_effective))
            st.code(f"Lat: {f_lat:.6f}\nLon: {f_lon:.6f}", language="json")
            if radius_effective <= 0:
                st.error(t("gps_risk"))
            else:
                st.info(f"{t('gps_safe')} {t('addr_obfuscated', r=radius_effective)}")
            st.button(t("btn_update_gps"), on_click=update_coordinates)

        st.divider()
        st.subheader(t("analysis_header"))

        # --- LOGIC HIỂN THỊ LỚP BẢO VỆ & BIỂU ĐỒ ---

        # 1. Tổng hợp thông tin các lớp bảo vệ (Protection Layers)
        age_req = st.session_state.z_age_required
        age_ver = st.session_state.age_verified
        zkp_on = st.session_state.zkp_active
        geo_on = st.session_state.geo_active
        # Lấy tên cấp độ mã hóa hiện tại
        depth_options = [t("depth_low"), t("depth_opt"), t("depth_high"), t("depth_max")]
        current_depth = depth_options[st.session_state.encryption_depth]

        # Tạo danh sách trạng thái để hiển thị
        layers_status = []
        layers_status.append(f"Z Age: {t('status_on') if age_req else t('status_off')}")
        if age_req:
            layers_status.append(f"18+: {t('status_ok') if age_ver else t('status_missing')}")
        layers_status.append(f"Z Face: {'Proof' if zkp_on else 'RAW'}")
        layers_status.append(f"Z Geo: {t('status_on') if geo_on else t('status_off')}")
        layers_status.append(f"Crypt: {current_depth}")

        # Hiển thị dòng tóm tắt các lớp bảo vệ (dùng key 'layer_info' trong từ điển)
        st.markdown(f"<span class='small-muted'>{t('layer_info', layers=' | '.join(layers_status))}</span>",
                    unsafe_allow_html=True)

        # --- 2. XỬ LÝ DỮ LIỆU LOG & BIỂU ĐỒ ---
        if st.session_state.logs:
            import re  # Thêm thư viện xử lý chuỗi

            # Tạo DataFrame từ logs gốc
            log_df = pd.DataFrame(st.session_state.logs)

            # === DỊCH TRẠNG THÁI & HÀNH ĐỘNG (Dữ liệu tĩnh) ===
            status_map = {
                "SUCCESS": t("log_stt_success"),
                "DANGER": t("log_stt_danger"),
                "TERMINATED": t("log_stt_term")
            }
            action_map = {"SYSTEM": t("log_act_sys")}

            # Thay thế dữ liệu tĩnh
            log_df["TrangThai"] = log_df["TrangThai"].replace(status_map)
            log_df["HanhDong"] = log_df["HanhDong"].replace(action_map)


            # === DỊCH CHI TIẾT (Dữ liệu động dùng Regex) ===
            def translate_dynamic_detail(text):
                # 1. Mẫu: "Proof <HASH> created"
                match_proof = re.search(r"Proof (.+) created", text)
                if match_proof:
                    return t("fmt_proof_created", id=match_proof.group(1))

                # 2. Mẫu: "Verified <HASH>"
                match_verify = re.search(r"Verified (.+)", text)
                if match_verify:
                    return t("fmt_verified", id=match_verify.group(1))

                # 3. Mẫu: "Sent RAW <SIZE> KB"
                match_raw = re.search(r"Sent RAW (.+) KB", text)
                if match_raw:
                    return t("fmt_raw_sent", size=match_raw.group(1))

                # 4. Mẫu: "Check Age: <AGE>"
                match_age = re.search(r"Check Age: (.+)", text)
                if match_age:
                    return t("fmt_check_age", age=match_age.group(1))

                # 5. Mẫu: "Spoofed radius <R>m"
                match_spoof = re.search(r"Spoofed radius (.+)m", text)
                if match_spoof:
                    return t("fmt_spoof", radius=match_spoof.group(1))

                # 6. Mẫu: "Force terminated <APP>"
                match_kill = re.search(r"Force terminated (.+)", text)
                if match_kill:
                    return t("fmt_force_kill", app=match_kill.group(1))

                # 7. Các trường hợp tĩnh (System Rebooted)
                if "System Rebooted" in text:
                    return t("log_desc_reboot")

                return text  # Trả về nguyên gốc nếu không khớp mẫu nào


            # Áp dụng hàm dịch cho từng dòng trong cột ChiTiet
            log_df["ChiTiet"] = log_df["ChiTiet"].apply(translate_dynamic_detail)
            # =========================================================

            # Hiển thị bảng
            st.dataframe(log_df, use_container_width=True, hide_index=True)

            def to_minute(ts: str) -> str:
                return str(ts)[:5]


            try:
                log_df["Minute"] = log_df["ThoiGian"].apply(to_minute)
                st.caption(t("chart1_title"))
                series = log_df.groupby("Minute").size().reset_index(name="Events")
                st.line_chart(series.set_index("Minute"))
            except Exception:
                pass

            st.caption(t("chart2_title"))
            status_counts = log_df["TrangThai"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"))

            st.caption(t("chart3_title"))
            action_counts = log_df["HanhDong"].value_counts().reset_index()
            action_counts.columns = ["Action", "Count"]
            st.bar_chart(action_counts.set_index("Action"))

        else:
            st.caption(t("log_empty"))

    # TAB 2: APP VIEW

    with tab2:
        app = st.session_state.target_app
        if not decision["allow_connection"]:
            st.error(t("app_disconnect", app=app))
        else:
            name = st.session_state.user_name or "User"
            age_ok = bool(st.session_state.age_verified) if st.session_state.z_age_required else True
            bio_ok = bool(st.session_state.latest_proof) and st.session_state.zkp_active

            bio_status = t("status_ok") if bio_ok else t("status_missing")
            if st.session_state.z_age_required:
                age_status = t("status_ok") if age_ok else t("status_missing")
            else:
                age_status = t("status_off")

            lines = [
                f"1) Biometric Proof: {bio_status}",
                f"2) Age Verify 18+: {age_status}",
                f"3) ID Document: {t('status_na')} (Fallback mode)"
            ]
            icon = "✓" if (age_ok or bio_ok) else "!"

            st.markdown(
                f"""
                <div class="white-app-view">
                    <div class="white-app-card">
                        <div class="big-check">{icon}</div>
                        <div class="app-lines">
                            <div><b>{t('app_view_title', app=app)}</b></div>
                            <div style="margin-top:14px;">{lines[0]}</div>
                            <div>{lines[1]}</div>
                            <div>{lines[2]}</div>
                        </div>
                        <div class="app-sub">{t('app_view_desc')}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# 8) FOOTER (NHẬT KÝ KIỂM TOÁN & EXPORT)

st.markdown("---")
st.subheader(t("log_header"))

if st.session_state.logs:
    import re

    # 1. Tạo DataFrame từ dữ liệu gốc
    footer_df = pd.DataFrame(st.session_state.logs)

    # 2. Định nghĩa các Map dịch (Giống Tab 1)
    status_map = {
        "SUCCESS": t("log_stt_success"),
        "DANGER": t("log_stt_danger"),
        "TERMINATED": t("log_stt_term")
    }
    action_map = {"SYSTEM": t("log_act_sys")}


    # 3. Hàm dịch chi tiết Dynamic (Giống Tab 1)
    def translate_footer_detail(text):
        # Mẫu 1: "Proof <HASH> created"
        match_proof = re.search(r"Proof (.+) created", text)
        if match_proof:
            return t("fmt_proof_created", id=match_proof.group(1))

        # Mẫu 2: "Verified <HASH>"
        match_verify = re.search(r"Verified (.+)", text)
        if match_verify:
            return t("fmt_verified", id=match_verify.group(1))

        # Mẫu 3: "Sent RAW <SIZE> KB"
        match_raw = re.search(r"Sent RAW (.+) KB", text)
        if match_raw:
            return t("fmt_raw_sent", size=match_raw.group(1))

        # Mẫu 4: "Check Age: <AGE>"
        match_age = re.search(r"Check Age: (.+)", text)
        if match_age:
            return t("fmt_check_age", age=match_age.group(1))

        # Mẫu 5: "Spoofed radius <R>m"
        match_spoof = re.search(r"Spoofed radius (.+)m", text)
        if match_spoof:
            return t("fmt_spoof", radius=match_spoof.group(1))

        # Mẫu 6: "Force terminated <APP>"
        match_kill = re.search(r"Force terminated (.+)", text)
        if match_kill:
            return t("fmt_force_kill", app=match_kill.group(1))

        # Mẫu 7: Tĩnh
        if "System Rebooted" in text:
            return t("log_desc_reboot")

        return text


    # 4. Áp dụng dịch vào DataFrame hiển thị
    footer_df["TrangThai"] = footer_df["TrangThai"].replace(status_map)
    footer_df["HanhDong"] = footer_df["HanhDong"].replace(action_map)
    footer_df["ChiTiet"] = footer_df["ChiTiet"].apply(translate_footer_detail)

    # 5. Hiển thị bảng đã dịch
    st.dataframe(footer_df, use_container_width=True, hide_index=True)

    # 6. Nút tải về (Vẫn tải dữ liệu gốc hoặc dữ liệu dịch tùy bạn chọn)
    # Ở đây tôi để tải dữ liệu đã dịch để báo cáo dễ đọc hơn
    csv_bytes = footer_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        t("btn_download"),
        data=csv_bytes,
        file_name="zshield_audit_logs.csv",
        mime="text/csv"
    )
else:
    st.text(t("log_safe"))