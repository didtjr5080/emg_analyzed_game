from game.controller import GameController


def test_score_only_changes_while_playing():
    controller = GameController()
    controller.add_score()
    assert controller.snapshot()["score"] == 0
    controller.set_game_state("start")
    assert controller.add_score()["score"] == 100


def test_pause_resume_and_reset():
    controller = GameController()
    controller.set_game_state("start")
    controller.set_game_state("pause")
    assert controller.snapshot()["game_state"] == "PAUSED"
    controller.update_emg(.8, .7, "slider")
    reset = controller.reset()
    assert reset["score"] == reset["fatigue"] == reset["game_time"] == 0
    assert reset["game_state"] == "READY"
    assert reset["input_mode"] == "slider"

