from pathlib import Path

ROOT = Path(__file__).resolve().parent

replacements = {
    "app/models/ddj.py": {
        "brand = Column(Enum(BrandEnum), default=BrandEnum.PIONEER)": "brand = Column(String(50), default='Pioneer')"
    },
    "app/models/audio.py": {
        "audio_type = Column(Enum(AudioTypeEnum), nullable=False)": "audio_type = Column(String(50), nullable=False)"
    },
    "app/models/music.py": {
        "genre = Column(Enum(GenreEnum), nullable=False, index=True)": "genre = Column(String(50), nullable=False, index=True)"
    },
    "app/models/preorder_set.py": {
        "set_type = Column(Enum(SetTypeEnum), nullable=False, index=True)": "set_type = Column(String(50), nullable=False, index=True)"
    },
    "app/models/course.py": {
        "difficulty = Column(Enum(DifficultyEnum), nullable=False, index=True)": "difficulty = Column(String(50), nullable=False, index=True)"
    },
    "app/models/order.py": {
        "status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.PENDING, index=True)": "status = Column(String(50), default='Pending', index=True)",
        "payment_method = Column(Enum(PaymentMethodEnum), nullable=True)": "payment_method = Column(String(50), nullable=True)"
    },
}

for relative_path, file_replacements in replacements.items():
    path = ROOT / relative_path

    if not path.exists():
        print(f"找不到檔案：{relative_path}")
        continue

    text = path.read_text(encoding="utf-8")

    changed = False
    for old, new in file_replacements.items():
        if old in text:
            text = text.replace(old, new)
            changed = True
            print(f"已修改：{relative_path}")
        else:
            print(f"未找到指定內容：{relative_path} -> {old}")

    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")

print("\n完成。請重新啟動 uvicorn。")