class MockLLM:


    def generate(
        self,
        prompt:str
    ):

        return {
            "analysis":
            "Potential brute force attack detected.",
            
            "recommendation":
            [
                "Check source IP reputation",
                "Review affected accounts",
                "Enable MFA"
            ]
        }