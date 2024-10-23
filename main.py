import pygame
import random
import os
import sys

# Global variable for highscore
highscore = None

class Tasot:
    """Class for levels"""
    def __init__(self, numero: int, kuvat: list):
        self.numero = numero    # Level number
        self.kuvat = kuvat      # List of images associated with the level
        self.kolikot = []       # List of coins
        self.hirviot = []       # List of monsters
        self.ovi_rect = None    # Exit door
        self.robo_rect = None   # Robot player
        self.lataa_taso(self.numero)

    # Load the level resources and initialize game objects.
    def lataa_taso(self, numero: int):
        x_robo = 0     # Initial x-coordinate for the robot
        y_robo = 50    # Initial y-coordinate for the robot
        self.robo_rect = pygame.Rect(x_robo, y_robo, self.kuvat[0].get_width(), self.kuvat[0].get_height())
        
        x_ovi = 800 - self.kuvat[1].get_width()   # X-coordinate for the exit door
        y_ovi = 650 - self.kuvat[1].get_height()  # Y-coordinate for the exit door
        self.ovi_rect = pygame.Rect(x_ovi, y_ovi, self.kuvat[1].get_width(), self.kuvat[1].get_height())    
        
        # Generate monsters and coins for the level
        self.hirviot = self.generoi_hirviot(numero)   # Generate monsters based on level
        self.kolikot = self.generoi_kolikot(5)     # Generate 5 coins

        pygame.display.flip()   # Update the display

    # Generate monsters based on the level number
    def generoi_hirviot(self, numero: int):
        hirviot = []     # List to hold monster rectangles
        hirvion_koordinaatit = []     # List to hold monster coordinates

        # Define monster coordinates for each level
        if numero == 1:
            hirvion_koordinaatit.append((800 - self.kuvat[1].get_width() - self.kuvat[2].get_width(), 650 - self.kuvat[2].get_height()))
            hirvion_koordinaatit.append((800 - self.kuvat[2].get_width(), 650 - self.kuvat[1].get_height() - self.kuvat[2].get_height()))
        elif numero == 2:
            for i in range(8):
                hirvion_koordinaatit.append((750 - self.kuvat[1].get_width() - self.kuvat[2].get_width(), 50 + self.kuvat[2].get_height()*i))
        elif numero == 3:
            for i in range(15):
                hirvion_koordinaatit.append((20 + self.kuvat[2].get_width()*i, 650 - self.kuvat[2].get_height() - self.kuvat[1].get_height()))
        elif numero == 4:
            for i in range(13):
                hirvion_koordinaatit.append((self.kuvat[2].get_width()*i, 650 - self.kuvat[2].get_height()*(1+i/2)))
            for i in range(4):
                hirvion_koordinaatit.append((600 + self.kuvat[2].get_width()*i, 650 - self.kuvat[2].get_height()*(1+i/2)))
        elif numero == 5:
            for i in range(7):
                hirvion_koordinaatit.append((200, 10 + self.kuvat[2].get_height()*i))
            for i in range(7):
                hirvion_koordinaatit.append((600, 650 - self.kuvat[2].get_height()*(i+1)))
            for i in range(3):
                hirvion_koordinaatit.append((800 - self.kuvat[2].get_width()*(i+1), 650 - self.kuvat[1].get_height() - self.kuvat[2].get_height()))
            for i in range(3):
                hirvion_koordinaatit.append((800 - self.kuvat[2].get_width()*(i+1), 650 - self.kuvat[2].get_height()*7))

        # Create rectangles for each monster using the defined coordinates        
        for x, y in hirvion_koordinaatit:
            hirviot.append(pygame.Rect(x, y, self.kuvat[2].get_width(), self.kuvat[2].get_height()))

        return hirviot   # Return the list of monster rectangles

    # Generate coins randomly on the level, ensuring no overlap with other objects
    def generoi_kolikot(self, maara: int):
        kolikot = []     # List to hold coin rectangles
        for _ in range(maara):
            while True:
                # Generate random coordinates for the coin
                x_kolikko = random.randint(0, 800 - self.kuvat[3].get_width())
                y_kolikko = random.randint(50, 650 - self.kuvat[3].get_height())
                kolikko_rect = pygame.Rect(x_kolikko, y_kolikko, self.kuvat[3].get_width(), self.kuvat[3].get_height())
                
                # Ensure the coin does not overlap with the robot, door, or existing monsters/coins
                if not any(kolikko_rect.colliderect(rect) for rect in [self.robo_rect, self.ovi_rect] + self.hirviot + kolikot):
                    kolikot.append(kolikko_rect)    # Add the coin if no overlap
                    break     # Exit the loop
        return kolikot    # Return the list of coin rectangles

class Paeta_laboratoriosta:
    """Main game class"""
    def __init__(self):
        pygame.init()     # Initialize Pygame

        self.naytto = pygame.display.set_mode((800, 700))       # Set window size
        pygame.display.set_caption("Paeta laboratoriosta")      # Window title

        self.fontti = pygame.font.SysFont("Arial", 24)    # Font for rendering text

        self.lataa_kuvat()   # Load images

        # Initialize player position and other variables
        self.x_robo = 0      # X position of the robot
        self.y_robo = 50     # Y position of the robot
        self.lompakko = 0    # Number of collected coins
        self.pausoitu = False     # Game paused flag
        self.pausotusaika = 0     # Time spent in pause
        self.pausoitu_start = 0   # Start time of the pause

        self.aloitus_aika = 0    # Game start time
        self.nykyinen_aika = 0   # Current time in the game
        self.nykyinen_taso = 0   # Current level

        self.lataa_rekordi()   # Load high score
        
        # Movement flags
        self.oikealle = False
        self.vasemmalle = False
        self.alas = False
        self.ylos = False
        
        self.kello = pygame.time.Clock()     # Clock to control frame rate

        self.taso = Tasot(1, self.kuvat)     # Create level object for the first level
        self.uusi_peli()        # Start a new game
        self.silmukka()         # Start the main game loop

    # Save the new record (highscore) to a file
    def tallenna_rekordi(self):
        if not os.path.exists("highscore.txt"):    # Check if highscore file exists
            with open("highscore.txt", "w") as f:
                f.write("0")     # Create file and write 0 if it doesn't exist

        with open("highscore.txt", "w") as f:
            f.write(str(highscore))     # Write the current highscore to the file

    # Load the highscore from a file
    def lataa_rekordi(self):
        global highscore
        if os.path.exists("highscore.txt"):        # Check if highscore file exists
            with open("highscore.txt", "r") as f:
                highscore = int(f.read())          # Read highscore from the file
        else:
            highscore = 0      # Set highscore to 0 if the file does not exist
    
    # Load all necessary images for the game
    """def lataa_kuvat(self):
        self.kuvat = []      # List to hold images
        for nimi in ["robo", "ovi", "hirvio", "kolikko"]:     # List of image file names
            # Load each image and append it to the list
            self.kuvat.append(pygame.image.load(os.path.join(os.path.dirname(__file__), nimi + ".png")))"""

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def lataa_kuvat(self):
        self.kuvat = []      # List to hold images
        for nimi in ["robo", "ovi", "hirvio", "kolikko"]:
            self.kuvat.append(pygame.image.load(self.resource_path(nimi + ".png")))

    # Start a new game
    def uusi_peli(self):
        self.x_robo = 0     # Reset robot's x position
        self.y_robo = 50    # Reset robot's y position
        self.lompakko = 0   # Reset collected coins

        # Movement flags
        self.oikealle = False
        self.vasemmalle = False
        self.alas = False
        self.ylos = False

        self.nykyinen_aika = 0     # Reset current time
        self.aloitus_aika = pygame.time.get_ticks()    # Record game start time
        self.nykyinen_taso = 1     # Reset level

        self.taso = Tasot(self.nykyinen_taso, self.kuvat)     # Load the level
        self.taso.lataa_taso(self.nykyinen_taso)
        
        self.naytto.fill((0, 0, 0))     # Fill the display with black
        pygame.display.flip()           # Update the display

    # Main game loop
    def silmukka(self):
        while True:                       # Run the game loop indefinitely
            self.tutki_tapahtumat()       # Check for events (input)
            if not self.pausoitu:     # If the game is not paused
                self.liiku()          # Move the robot
                self.tormays()        # Check for collisions and interactions

            self.paivita_naytto()     # Update the display
            pygame.display.flip()     # Refresh the screen
            self.kello.tick(60)       # Limit frame rate to 60 FPS

    # Draw items on the screen
    def paivita_naytto(self):
        self.naytto.fill((0, 0, 255))     # Fill the display with blue
        self.naytto.blit(self.kuvat[0], (self.x_robo, self.y_robo))     # Draw the robot
        self.naytto.blit(self.kuvat[1], (self.taso.ovi_rect.x, self.taso.ovi_rect.y))     # Draw the door
        
        for hirvio_rect in self.taso.hirviot:     # Draw each monster
            self.naytto.blit(self.kuvat[2], (hirvio_rect.x, hirvio_rect.y))
        
        for kolikko_rect in self.taso.kolikot:     # Draw each coin
            self.naytto.blit(self.kuvat[3], (kolikko_rect.x, kolikko_rect.y))

        if self.pausoitu:     # If the game is paused
            fontti = pygame.font.SysFont("Arial", 50)     # Load font
            teksti = fontti.render("PAUSOITU", True, (255, 0, 0))   # Render pause text
            self.naytto.blit(teksti, (400 - teksti.get_width() // 2, 350 - teksti.get_height() // 2))  # Center the pause text

        self.piirra_naytto()   # Call to draw additional UI elements

    # Move the robot based on current input
    def liiku(self):
        if self.oikealle and self.x_robo < 800 - self.kuvat[0].get_width():   # Move right if not at screen edge
            self.x_robo += 2
        if self.vasemmalle and self.x_robo > 0:   # Move left if not at screen edge
            self.x_robo -= 2
        if self.alas and self.y_robo < 650 - self.kuvat[0].get_height():   # Move down if not at screen edge
            self.y_robo += 2
        if self.ylos and self.y_robo > 50:   # Move up if not at screen edge
            self.y_robo -= 2

        self.taso.robo_rect.topleft = (self.x_robo, self.y_robo)   # Update robot's rectangle position

    # Check for input events
    def tutki_tapahtumat(self):
        for tapahtuma in pygame.event.get():     # Process each event
            if tapahtuma.type == pygame.KEYDOWN:   # Key press event
                if tapahtuma.key == pygame.K_LEFT:    # Move left
                    self.vasemmalle = True
                if tapahtuma.key == pygame.K_RIGHT:   # Move right
                    self.oikealle = True
                if tapahtuma.key == pygame.K_UP:      # Move up
                    self.ylos = True
                if tapahtuma.key == pygame.K_DOWN:    # Move down
                    self.alas = True

                if tapahtuma.key == pygame.K_F2:      # Restart the game
                    self.uusi_peli()

                if tapahtuma.key == pygame.K_ESCAPE:  # Quit the game
                    exit()

                if tapahtuma.key == pygame.K_SPACE:     # Pause or unpause the game
                    self.pausoitu = not self.pausoitu
                    if self.pausoitu:     # If paused
                        self.pausoitu_start = pygame.time.get_ticks()   # Record pause start time
                    else:                 # If unpaused
                        self.pausotusaika += pygame.time.get_ticks() - self.pausoitu_start   # Calculate total pause time

            if tapahtuma.type == pygame.KEYUP:     # Key release event
                if tapahtuma.key == pygame.K_LEFT:     # Stop moving left
                    self.vasemmalle = False
                if tapahtuma.key == pygame.K_RIGHT:    # Stop moving right
                    self.oikealle = False
                if tapahtuma.key == pygame.K_UP:       # Stop moving up
                    self.ylos = False
                if tapahtuma.key == pygame.K_DOWN:     # Stop moving down
                    self.alas = False

            if tapahtuma.type == pygame.QUIT:     # Quit event
                exit()

    # Check for collisions and interactions with the game world
    def tormays(self):
        global highscore

        # Check if the robot reaches the door
        if self.taso.robo_rect.colliderect(self.taso.ovi_rect):
            # Load font and text for door messages
            oven_fontti = pygame.font.SysFont("Arial", 20)
            oven_teksti = oven_fontti.render("Onnea! Taso suoritettu!", True, (255, 0, 0))
            sirry_teksti = oven_fontti.render("Paina Enter siirtyäksesi seuraavalle tasolle", True, (255, 0, 0))
            tekstin_rect1 = oven_teksti.get_rect(center=(400, 330))
            tekstin_rect2 = sirry_teksti.get_rect(center=(400, 370))
            # Draw message
            self.naytto.blit(oven_teksti, (tekstin_rect1))
            self.naytto.blit(sirry_teksti, (tekstin_rect2))
            pygame.display.flip()   # Refresh the display

            self.nykyinen_taso += 1   # Increment level

            while True:     # Wait for player input to proceed
                for tapahtuma in pygame.event.get():     # Process events
                    if tapahtuma.type == pygame.QUIT:      # Quit event
                        pygame.quit()
                        exit()

                    if tapahtuma.type == pygame.KEYDOWN:   # Key press event
                        if tapahtuma.key == pygame.K_RETURN:   # Move to next level
                            if self.nykyinen_taso <= 5:     # If still within levels
                                self.x_robo = 0     # Reset robot position
                                self.y_robo = 50
                                self.lompakko = 0   # Reset collected coins
                                # Reset movement flags
                                self.oikealle = False
                                self.vasemmalle = False
                                self.ylos = False
                                self.alas = False
                                self.taso.lataa_taso(self.nykyinen_taso)   # Load the next level
                                pygame.display.flip()   # Refresh display
                                return   # Exit this function
                            else:     # If all levels completed
                                self.naytto.fill((0, 0, 0))     # Fill display with black
                                suoritettu_fontti = pygame.font.SysFont("Arial", 20)   # Load font for completion message
                                suoritettu_teksti = suoritettu_fontti.render("Onnea! Peli suoritettu!", True, (255, 0, 0))   # Completion message
                                valinta_teksti = suoritettu_fontti.render("F2-uusi peli   Esc-sulje peli", True, (255, 0, 0))   # Restart and exit options
                                tekstiin1_rect = suoritettu_teksti.get_rect(center=(400, 330))   # Center the completion message
                                tekstiin2_rect = valinta_teksti.get_rect(center=(400, 370))   # Center the options message
            
                                if highscore > self.nykyinen_aika or highscore == 0:   # Refresh highscore   
                                    highscore = self.nykyinen_aika
                                    self.tallenna_rekordi()
                                    # Draw text if the highscore was refreshing
                                    ennatys_fontti = pygame.font.SysFont("Arial", 50)
                                    minuutit_highscore = highscore // 60
                                    sekunnit_highscore = highscore % 60
                                    highscore_text = f"{minuutit_highscore:02}:{sekunnit_highscore:02}"
                                    ennatys_teksti = ennatys_fontti.render("Uusi ennatysaika: " + highscore_text, True, (255, 0, 0))
                                    self.naytto.blit(ennatys_teksti, (400 - ennatys_teksti.get_width()/2, 100))
                                
                                self.naytto.blit(suoritettu_teksti, (tekstiin1_rect))   # Draw completion message
                                self.naytto.blit(valinta_teksti, (tekstiin2_rect))   # Draw options message
                                pygame.display.flip()   # Refresh display

                                while True:     # Wait for player input
                                    for tapahtuma in pygame.event.get():   # Process events
                                        if tapahtuma.type == pygame.QUIT:   # Quit event
                                            pygame.quit()
                                            exit()

                                        if tapahtuma.type == pygame.KEYDOWN:   # Key press event
                                            if tapahtuma.key == pygame.K_F2:   # Restart the game
                                                self.uusi_peli()
                                                self.silmukka()

                                            if tapahtuma.key == pygame.K_ESCAPE:   # Quit the game
                                                exit()

        # Check for collisions with monsters
        for hirvio in self.taso.hirviot:
            if self.taso.robo_rect.colliderect(hirvio):   # If robot collides with a monster
                # Prepare and print the text
                hirvion_fontti = pygame.font.SysFont("Arial", 20)
                hirvion_teksti1 = hirvion_fontti.render("Maksaa 10 kolikkoa, karkottaaksesi hirvion?", True, (255, 0, 0))
                hirvion_teksti2 = hirvion_fontti.render("Y - kyllä, N - ei", True, (255, 0, 0))

                tekstin1_rect = hirvion_teksti1.get_rect(center=(400, 330))
                tekstin2_rect = hirvion_teksti2.get_rect(center=(400, 370))
                self.naytto.blit(hirvion_teksti1, tekstin1_rect)
                self.naytto.blit(hirvion_teksti2, tekstin2_rect)

                pygame.display.flip()   # Refresh display

                while True:
                    for tapahtuma in pygame.event.get():   # Wait for player input
                        if tapahtuma.type == pygame.QUIT:   # Quit event
                            pygame.quit()
                            exit()

                        if tapahtuma.type == pygame.KEYDOWN:   # Key press event
                            if tapahtuma.key == pygame.K_y:   # If player's answer is "yes"
                                if self.lompakko >= 10:   # If coins is enought to pay
                                    self.lompakko -= 10   # Decrease collected coins on a 10
                                    self.taso.hirviot.remove(hirvio)   # Delete the gost
                                    self.oikealle = False
                                    self.vasemmalle = False
                                    self.ylos = False
                                    self.alas = False
                                    return
                                else:   # If coins is not enought to pay
                                    self.x_robo = 0   # Robot goes to the start position
                                    self.y_robo = 50
                                    self.oikealle = False
                                    self.vasemmalle = False
                                    self.ylos = False
                                    self.alas = False
                                    return
                            if tapahtuma.key == pygame.K_n:   # If player's answer is "no"
                                self.x_robo = 0   # Robot goes to the start position
                                self.y_robo = 50
                                self.oikealle = False
                                self.vasemmalle = False
                                self.ylos = False
                                self.alas = False
                                return

        # Check for collected coins
        for kolikko in self.taso.kolikot[:]:
            if self.taso.robo_rect.colliderect(kolikko):   # If robot collides with a coin
                self.taso.kolikot.remove(kolikko)   # Remove the collected coin
                self.lompakko += 1   # Increase collected coins

                uusi_kolikko = self.taso.generoi_kolikot(1)
                self.taso.kolikot.extend(uusi_kolikko)
    
    # Draws the screen's details            
    def piirra_naytto(self):
        # If game is not paused count and draw timer
        if not self.pausoitu:
            self.nykyinen_aika = (pygame.time.get_ticks() - self.aloitus_aika - self.pausotusaika) // 1000
        minuutit = self.nykyinen_aika // 60
        sekunnit = self.nykyinen_aika % 60
        timer_text = f"Taso {self.nykyinen_taso}: {minuutit:02}:{sekunnit:02}"
        aika_txt = self.fontti.render(timer_text, True, (255, 0, 0))
        self.naytto.blit(aika_txt, (10, 10))

        # Draw the coins number
        lompakko_txt = self.fontti.render("Kolikot: ", True, (255, 0, 0))
        lompakko_num = self.fontti.render(str(self.lompakko), True, (255, 0, 0))
        self.naytto.blit(lompakko_txt, (400-lompakko_txt.get_width()/2, 10))
        self.naytto.blit(lompakko_num, (400+lompakko_txt.get_width()/2+10, 10))

        # Draw the best time at local computer
        ennatys_txt = self.fontti.render("Ennätysaika: ", True, (255, 0, 0))
        minuutit_highscore = highscore // 60
        sekunnit_highscore = highscore % 60
        highscore_text = f"{minuutit_highscore:02}:{sekunnit_highscore:02}"
        ennatys_num = self.fontti.render(highscore_text, True, (255, 0, 0))
        self.naytto.blit(ennatys_txt, (800-ennatys_txt.get_width()-ennatys_num.get_width()-60, 10))
        self.naytto.blit(ennatys_num, (800-ennatys_num.get_width()-50, 10))

        # Draw help menu
        uusi_fontti = self.fontti.render("F2 = uusi peli", True, (255, 0, 0))
        ulos_fontti = self.fontti.render("Esc = sulje peli", True, (255, 0, 0))
        paus_fontti = self.fontti.render("Space = pausoida", True, (255, 0, 0))

        pygame.draw.rect(self.naytto, (0, 0, 0), (0, 650, 800, 50))
        self.naytto.blit(uusi_fontti, (50, 660))
        self.naytto.blit(ulos_fontti, (400-ulos_fontti.get_width()/2, 660))
        self.naytto.blit(paus_fontti, (800-paus_fontti.get_width()-50, 660))
        pygame.display.flip()

# Run the game
if __name__ == "__main__":
    Paeta_laboratoriosta()    # Create game instance and start