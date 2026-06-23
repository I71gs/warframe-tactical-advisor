def register_plugin(registry):
    def test_cmd():
        print("SDK Sample command triggered!")
        
    registry.register_command("Developer SDK: Trigger Test", test_cmd)
