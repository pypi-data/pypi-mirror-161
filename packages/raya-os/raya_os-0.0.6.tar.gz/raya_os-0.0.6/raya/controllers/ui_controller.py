class UIController(BasePseudoController): 

    async def display_modal(self, subtitle: str, content: str = None, 
                        title: str = None, 
                        modal_type: MODAL_TYPE = MODAL_TYPE.INFO, 
                        submit_text: str = "Yes", cancel_text: str = "No",
                        wait: bool = True, callback: callable = None):
            pass


    async def display_screen(self, title: str, subtitle: str = None,
                              show_loader: bool = True,
                              theme: THEME_TYPE = THEME_TYPE.DARK) -> Enum: 
            pass

            
    async def display_interactive_map(self, title: str, subtitle: str = None,
                                        map_name: str = None, show_robot_position: bool = True,
                                        view_only: bool = False, theme: THEME_TYPE = THEME_TYPE.DARK,
                                        wait:bool = True, callback: callable = None)-> Enum:
            pass
    

    async def display_action_screen(self, title: str, button_text: str, 
                              subtitle: str = None, button_size: str = None,
                              theme: THEME_TYPE = THEME_TYPE.DARK,
                              wait:bool =True, callback:callable = None) -> Enum: 
            pass


    async def display_input_modal(self, subtitle: str, title: str, 
                                  submit_text: str, cancel_text: str,
                                  placeholder: str = None, 
                                  input_type: INPUT_TYPE = INPUT_TYPE.TEXT,
                                  wait: bool = True, callback: callable = None): 
            pass


    async def display_choice_selector(self, data: list, 
                                      custom_cards_style: dict = None,
                                      title: str = None, 
                                      theme: THEME_TYPE = THEME_TYPE.DARK, 
                                      show_back_button: bool = False,
                                      wait:bool = True, callback:callable = None) \
                                                                            -> Enum:
            pass