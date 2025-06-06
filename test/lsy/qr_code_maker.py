import qrcode

text = input("QR코드로 만들 텍스트: ")
img = qrcode.make(text)
img.save("my_qrcode.png")
print("QR코드가 'my_qrcode.png'로 저장되었습니다.")
