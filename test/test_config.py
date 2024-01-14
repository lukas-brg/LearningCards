from carddown_parser.config import Config


def test_config_singleton():
    conf = Config.get_config()
    conf2 = Config.get_config()

    assert conf is conf2

    can_instantiate = False
    try:
        Config()
        can_instantiate = True
    except:
        pass
    
    assert not can_instantiate
