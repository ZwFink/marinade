import marinade as md

def test_marinade():
    a = 25
    b = 30
    c = 45
    md.mark_region_begin("test_marinade")
    d = a + b + c
    print(f"d: {d}")
    md.mark_region_end("test_marinade")
    md.replay_region("test_marinade")

test_marinade()
md.replay_region("test_marinade")