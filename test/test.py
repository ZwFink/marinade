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

def test_loop():
    total_iters = 5
    executed_iters = 0
    md.mark_region_begin("test_loop")
    for i in range(total_iters):
        executed_iters += 1
    print(f"executed_iters: {executed_iters}")
    md.mark_region_end("test_loop")
    md.replay_region("test_loop", overrides = {'total_iters': 10})


test_marinade()
test_loop()