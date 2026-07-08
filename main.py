import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import customtkinter as ctk
from PIL import Image, ImageTk

#tema interfatei
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AplicatieGesti(ctk.CTk):
    def __init__(self):
        super().__init__()

        # fereastra principala
        self.title("Controller PC Inteligent - Dashboard")
        self.geometry("1100x650")
        self.resizable(False, False)

        # initiere variabile 
        self.marja = 100
        self.factor_netezire = 5
        self.loc_curenta_x, self.loc_curenta_y = 0, 0
        self.loc_veche_x, self.loc_veche_y = 0, 0
        self.click_apasat = False
        self.dublu_click_apasat = False
        self.click_dreapta_apasat = False
        self.loc_veche_scroll_y = 0
        self.loc_veche_scroll_x = 0
        self.screenshot_luat = False
        
        self.fereastra_manual = None 

        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.ecran_l, self.ecran_i = pyautogui.size()
        
        self.cap = cv2.VideoCapture(0)
        self.cam_l = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_i = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # interfata UI 
        self.frame_video = ctk.CTkFrame(self, width=660, height=500)
        self.frame_video.grid(row=0, column=0, padx=20, pady=20, sticky="nw")
        
        self.label_video = ctk.CTkLabel(self.frame_video, text="")
        self.label_video.pack(padx=10, pady=10)

        self.frame_setari = ctk.CTkFrame(self, width=350, height=500)
        self.frame_setari.grid(row=0, column=1, padx=20, pady=20, sticky="ne")

        self.titlu_setari = ctk.CTkLabel(self.frame_setari, text="Panou de Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.titlu_setari.pack(pady=20)

        self.label_marja = ctk.CTkLabel(self.frame_setari, text=f"Zona de confort (Marja): {self.marja}")
        self.label_marja.pack(pady=(20, 0))
        self.slider_marja = ctk.CTkSlider(self.frame_setari, from_=10, to=150, command=self.schimba_marja)
        self.slider_marja.set(self.marja)
        self.slider_marja.pack(pady=10)

        self.label_netezire = ctk.CTkLabel(self.frame_setari, text=f"Fluiditate (Netezire): {self.factor_netezire}")
        self.label_netezire.pack(pady=(20, 0))
        self.slider_netezire = ctk.CTkSlider(self.frame_setari, from_=1, to=15, number_of_steps=14, command=self.schimba_netezire)
        self.slider_netezire.set(self.factor_netezire)
        self.slider_netezire.pack(pady=10)

        self.label_status = ctk.CTkLabel(self.frame_setari, text="Status: ACTIV", text_color="green", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_status.pack(pady=20)

        self.buton_manual = ctk.CTkButton(self.frame_setari, text="📖 Ghid de Utilizare", fg_color="#1f538d", hover_color="#14375e", command=self.deschide_manual)
        self.buton_manual.pack(pady=10)

        self.buton_inchidere = ctk.CTkButton(self.frame_setari, text="Inchide Aplicatia", fg_color="red", hover_color="darkred", command=self.inchide_aplicatia)
        self.buton_inchidere.pack(side="bottom", pady=20)

        #pornirea camerei web 
        self.update_video()

    # functii pentru UI 
    def schimba_marja(self, valoare):
        self.marja = int(valoare)
        self.label_marja.configure(text=f"Zona de confort (Marja): {self.marja}")

    def schimba_netezire(self, valoare):
        self.factor_netezire = int(valoare)
        self.label_netezire.configure(text=f"Fluiditate (Netezire): {self.factor_netezire}")

    def inchide_aplicatia(self):
        self.cap.release()
        self.destroy()

    #functie pentru meniu de gesturi 
    def deschide_manual(self):
        if self.fereastra_manual is None or not self.fereastra_manual.winfo_exists():
            self.fereastra_manual = ctk.CTkToplevel(self)
            self.fereastra_manual.title("Dictionar de Gesturi")
            self.fereastra_manual.geometry("450x500")
            self.fereastra_manual.resizable(False, False)
            self.fereastra_manual.attributes("-topmost", True) 
            
            scroll_frame = ctk.CTkScrollableFrame(self.fereastra_manual, width=400, height=450)
            scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

            titlu = ctk.CTkLabel(scroll_frame, text="Cum sa folosesti Controller-ul", font=ctk.CTkFont(size=20, weight="bold"))
            titlu.pack(pady=(0, 20))

            # lista gesturi 
            gesturi = [
                ("🖱️ Miscare Mouse", "Foloseste DOAR degetul aratator."),
                ("🟢 Click Stanga", "Ciupeste: Degetul Mare + Mijlociu."),
                ("🔵 Dublu Click", "Ciupeste: Degetul Mare + Inelar."),
                ("🟠 Click Dreapta", "Ciupeste: Degetul Mare + Degetul Mic."),
                ("🟡 Scroll & Zoom", "Ciupeste: Degetul Mare + Aratator.\n• Misca mana sus/jos pentru Scroll.\n• Misca mana stanga/dreapta pentru Zoom."),
                ("📸 Screenshot", "Gestul 'Rock' (Aratator + Deget Mic ridicate).\nSalvează poza în PC."),
                ("⏸️ Standby (Pauză)", "Strange pumnul complet.\nCursorul ingheata pana redeschizi palma.")
            ]

            for titlu_gest, descriere in gesturi:
                lbl_titlu = ctk.CTkLabel(scroll_frame, text=titlu_gest, font=ctk.CTkFont(size=16, weight="bold"), text_color="#00a8ff")
                lbl_titlu.pack(anchor="w", pady=(10, 0))
                lbl_desc = ctk.CTkLabel(scroll_frame, text=descriere, justify="left")
                lbl_desc.pack(anchor="w", padx=20, pady=(0, 10))
        else:
            self.fereastra_manual.focus()

    
    def update_video(self):
        succes, frame = self.cap.read()
        if succes:
            frame = cv2.flip(frame, 1)
            
            limita_jos = self.cam_i - self.marja - 80 
            
            cv2.rectangle(frame, (self.marja, self.marja), (self.cam_l - self.marja, limita_jos), (255, 0, 255), 2)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rezultat = self.hands.process(frame_rgb)

            status_curent = "ACTIV"
            culoare_status = "green"

            if rezultat.multi_hand_landmarks:
                for hand_landmarks in rezultat.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    aratator_sus = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
                    mijlociu_sus = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
                    inelar_sus = hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y
                    mic_sus = hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y

                    degete_ridicate = sum([aratator_sus, mijlociu_sus, inelar_sus, mic_sus])

                    pct_8 = hand_landmarks.landmark[8]   
                    pct_4 = hand_landmarks.landmark[4]   
                    pct_12 = hand_landmarks.landmark[12] 
                    pct_16 = hand_landmarks.landmark[16] 
                    pct_20 = hand_landmarks.landmark[20] 
                    
                    x8, y8 = int(pct_8.x * self.cam_l), int(pct_8.y * self.cam_i)
                    x4, y4 = int(pct_4.x * self.cam_l), int(pct_4.y * self.cam_i)
                    x12, y12 = int(pct_12.x * self.cam_l), int(pct_12.y * self.cam_i)
                    x16, y16 = int(pct_16.x * self.cam_l), int(pct_16.y * self.cam_i)
                    x20, y20 = int(pct_20.x * self.cam_l), int(pct_20.y * self.cam_i) 

                    x_palma = int(hand_landmarks.landmark[0].x * self.cam_l)
                    y_palma = int(hand_landmarks.landmark[0].y * self.cam_i)

                    distanta_scroll = math.hypot(x8 - x4, y8 - y4) 
                    distanta_click = math.hypot(x12 - x4, y12 - y4) 
                    distanta_dublu = math.hypot(x16 - x4, y16 - y4) 
                    distanta_dreapta = math.hypot(x20 - x4, y20 - y4) 

                    if not (aratator_sus and not mijlociu_sus and not inelar_sus and mic_sus):
                        self.screenshot_luat = False

                    # 1. standby
                    if degete_ridicate == 0:
                        status_curent = "STANDBY"
                        culoare_status = "red"
                        self.loc_veche_scroll_y = y_palma 
                        self.loc_veche_scroll_x = x_palma 

                    # 2. screenshot
                    elif aratator_sus and not mijlociu_sus and not inelar_sus and mic_sus:
                        status_curent = "SCREENSHOT"
                        culoare_status = "white"
                        if not self.screenshot_luat:
                            pyautogui.hotkey('win', 'prtsc') 
                            self.screenshot_luat = True
                        self.loc_veche_scroll_y = y_palma 
                        self.loc_veche_scroll_x = x_palma 

                    # 3. scroll + zoom
                    elif distanta_scroll < 40:
                        cv2.circle(frame, (x8, y8), 15, (0, 255, 255), cv2.FILLED) 
                        diferenta_y = self.loc_veche_scroll_y - y_palma 
                        diferenta_x = x_palma - self.loc_veche_scroll_x 
                        
                        if abs(diferenta_y) > abs(diferenta_x):
                            status_curent = "SCROLL MODE"
                            culoare_status = "orange"
                            if abs(diferenta_y) > 5: pyautogui.scroll(diferenta_y * 4) 
                        else:
                            status_curent = "ZOOM MODE"
                            culoare_status = "yellow"
                            if abs(diferenta_x) > 5:
                                pyautogui.keyDown('ctrl') 
                                pyautogui.scroll(diferenta_x * 4) 
                                pyautogui.keyUp('ctrl') 
                                
                        self.loc_veche_scroll_y = y_palma 
                        self.loc_veche_scroll_x = x_palma 
                    
                    # 4. normal (miscari + click)
                    else:
                        self.loc_veche_scroll_y = y_palma 
                        self.loc_veche_scroll_x = x_palma 
                        cv2.circle(frame, (x8, y8), 15, (255, 0, 255), cv2.FILLED)
                        
                        x_ecran = np.interp(x8, (self.marja, self.cam_l - self.marja), (0, self.ecran_l))
                        y_ecran = np.interp(y8, (self.marja, limita_jos), (0, self.ecran_i))
                        
                        if not (distanta_click < 70 or distanta_dublu < 70 or distanta_scroll < 70 or distanta_dreapta < 70):
                            self.loc_curenta_x = self.loc_veche_x + (x_ecran - self.loc_veche_x) / self.factor_netezire
                            self.loc_curenta_y = self.loc_veche_y + (y_ecran - self.loc_veche_y) / self.factor_netezire
                            pyautogui.moveTo(self.loc_curenta_x, self.loc_curenta_y)
                            self.loc_veche_x, self.loc_veche_y = self.loc_curenta_x, self.loc_curenta_y

                        if distanta_click < 40:
                            cv2.circle(frame, (x12, y12), 15, (0, 255, 0), cv2.FILLED) 
                            status_curent = "CLICK STANGA"
                            culoare_status = "green"
                            if not self.click_apasat:
                                pyautogui.click()
                                self.click_apasat = True
                        else: self.click_apasat = False
                            
                        if distanta_dublu < 40:
                            cv2.circle(frame, (x16, y16), 15, (255, 0, 0), cv2.FILLED) 
                            status_curent = "DUBLU CLICK"
                            culoare_status = "blue"
                            if not self.dublu_click_apasat:
                                pyautogui.doubleClick()
                                self.dublu_click_apasat = True
                        else: self.dublu_click_apasat = False

                        if distanta_dreapta < 40:
                            cv2.circle(frame, (x20, y20), 15, (0, 165, 255), cv2.FILLED) 
                            status_curent = "CLICK DREAPTA"
                            culoare_status = "cyan"
                            if not self.click_dreapta_apasat:
                                pyautogui.rightClick()
                                self.click_dreapta_apasat = True
                        else: self.click_dreapta_apasat = False

            self.label_status.configure(text=f"Status: {status_curent}", text_color=culoare_status)

            frame_final = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            imagine_pil = Image.fromarray(frame_final)
            imagine_tk = ctk.CTkImage(light_image=imagine_pil, dark_image=imagine_pil, size=(640, 480))
            
            self.label_video.configure(image=imagine_tk)
            self.label_video.image = imagine_tk 

        self.after(15, self.update_video)

if __name__ == "__main__":
    app = AplicatieGesti()
    app.mainloop()