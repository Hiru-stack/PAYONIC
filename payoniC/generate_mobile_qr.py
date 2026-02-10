import qrcode
import os

url = "https://192.168.184.56:5000"
img = qrcode.make(url)

# Save to artifacts directory
save_path = r"C:\Users\User\.gemini\antigravity\brain\fcf49729-6584-4517-8b9a-55a3d62b95b7\mobile_qr.png"
img.save(save_path)
print(f"QR code saved to {save_path}")
