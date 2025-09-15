import numpy as np
import pandas as pd

def tao_du_lieu_marketing(n=100, random_state=42):
    np.random.seed(random_state)

    # Chi phí quảng cáo (triệu VND)
    chi_phi_qc = np.random.uniform(50, 500, n)

    # Lượt xem ~ tỉ lệ với chi phí + noise
    luot_xem = chi_phi_qc * np.random.uniform(80, 120) + np.random.normal(0, 5000, n)

    # Lượt click ~ tỷ lệ với lượt xem + noise
    luot_click = luot_xem * np.random.uniform(0.01, 0.05) + np.random.normal(0, 200, n)

    # Khách hàng mới ~ tỷ lệ với lượt click + noise
    khach_hang_moi = luot_click * np.random.uniform(0.05, 0.15) + np.random.normal(0, 20, n)

    # Doanh thu ~ Chi phí QC + Khách hàng mới + noise
    doanh_thu = chi_phi_qc * 1.5 + khach_hang_moi * 10 + np.random.normal(0, 1000, n)

    df = pd.DataFrame({
        "ChiPhiQC": chi_phi_qc.round(2),
        "LuotXem": luot_xem.round(0),
        "LuotClick": luot_click.round(0),
        "KhachHangMoi": khach_hang_moi.round(0),
        "DoanhThu": doanh_thu.round(2),
    })

    return df

if __name__ == "__main__":
    df = tao_du_lieu_marketing(200)
    print(df.head())

    # Lưu ra file CSV để test
    df.to_csv("du_lieu_marketing_gia.csv", index=False, encoding="utf-8-sig")
    print("✅ Đã tạo file du_lieu_marketing_gia.csv")
