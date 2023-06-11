import random
import customtkinter
import numpy as np
import customtkinter as tk
from tkinter import messagebox, ttk
import tkinter


# Dostępne zajęcia
classes = [
    "Matematyka",
    "Historia",
    "Język angielski",
    "Fizyka",
    "Biologia",
    "Chemia",
    "Wychowanie fizyczne"
]

# Dostępne dni tygodnia i godziny
days = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]
hours = ["8:00-9:30", "9:45-11:15", "11:30-13:00", "14:00-15:30"]

# Ograniczenia planowania zajęć
# preferences = {}

# Parametry algorytmu genetycznego
population_size = 100
generations = 500
mutation_rate = 0.8
crossover_rate = 0.5

# Słownik preferencji zajęć
preferences = {}

# Funkcja do wyświetlania planu zajęć w tabeli
def display_schedule(schedule):
    for widget in schedule_frame.winfo_children():
        widget.destroy()

    # Wyświetlanie dni na górze tabeli
    for day in range(len(days)):
        day_label = tk.CTkLabel(schedule_frame, text=days[day], width=15, anchor="center")
        day_label.grid(row=0, column=day + 1, padx=2, pady=2)

    # Wyświetlanie godzin po lewej stronie tabeli
    for hour in range(len(hours)):
        hour_label = tk.CTkLabel(schedule_frame, text=hours[hour], width=15, anchor="center")
        hour_label.grid(row=hour + 1, column=0, padx=2, pady=2)

    # Wyświetlanie zajęć w kratkach
    for day in range(len(days)):
        for hour in range(len(hours)):
            class_label = tk.CTkLabel(schedule_frame, text=schedule[day][hour], width=15, height=2)
            class_label.grid(row=hour + 1, column=day + 1, padx=2, pady=2)

# Funkcja uruchamiająca algorytm genetyczny po kliknięciu przycisku
def generate_schedule():
    try:
        update_parameters()
        best_schedule = genetic_algorithm()
        display_schedule(best_schedule)
    except Exception as e:
        print(e)

# Funkcja do obsługi zdarzenia kliknięcia przycisku "Powrót"
# def return_to_preferences():
#     schedule_frame.pack_forget()  # Ukrycie kontenera z planem zajęć
#     return_button.pack_forget()  # Ukrycie przycisku powrotu
#     generate_button.pack(side=tk.LEFT, padx=5)  # Wyświetlenie przycisku generowania na lewo
#     import_button.pack(side=tk.LEFT, padx=5)  # Wyświetlenie przycisku importowania na lewo
#     preferences_frame.pack()  # Wyświetlenie kontenera z dodawaniem ograniczeń

# Funkcja do obsługi zdarzenia kliknięcia przycisku "Dodaj preferencje"
def add_preferences():
    subject = subject_var.get()
    selected_hours = [hours[i] for i in range(len(hours)) if hours_vars[i].get() == 1]
    selected_days = [days[i] for i in range(len(days)) if days_vars[i].get() == 1]
    preferences[subject] = (selected_days, selected_hours)
    display_preferences()

# Funkcja do obsługi zdarzenia kliknięcia przycisku "Usuń preferencję"
def remove_preference():
    selected_item = preferences_tree.focus()
    if selected_item:
        subject = preferences_tree.item(selected_item, "values")[0]
        del preferences[subject]
        display_preferences()

# Funkcja do obsługi zdarzenia kliknięcia przycisku "Usuń wszystkie preferencje"
def remove_all_preferences():
    preferences.clear()
    display_preferences()

# Funkcja do wyświetlania preferencji zajęć w interfejsie graficznym
def display_preferences():
    preferences_tree.delete(*preferences_tree.get_children())
    for subject, prefs in preferences.items():
        days, hours = prefs
        preferences_tree.insert("", tk.END, values=(subject, days, hours))

# Funkcja do aktualizacji parametrów algorytmu genetycznego
def update_parameters():
    global population_size, generations, mutation_rate, crossover_rate
    population_size = int(population_size_entry.get())
    generations = int(generations_entry.get())
    mutation_rate = float(mutation_rate_entry.get())
    crossover_rate = float(crossover_rate_entry.get())

# Generowanie początkowej populacji
def generate_initial_population():
    population = []
    class_counts = {c: 0 for c in classes}
    max_class_count = population_size // len(classes)

    for _ in range(population_size):
        schedule = np.empty((len(days), len(hours)), dtype=object)

        # Reset the class_counts for each schedule
        current_class_counts = class_counts.copy()

        # Fill the schedule with equal number of each class
        for day in range(len(days)):
            for hour in range(len(hours)):
                available_classes = [c for c, count in current_class_counts.items() if count < max_class_count]

                # Check if there are available classes to assign
                if len(available_classes) == 0:
                    # If no available classes, reset the class_counts and try again
                    current_class_counts = class_counts.copy()
                    available_classes = [c for c, count in current_class_counts.items() if count < max_class_count]

                selected_class = random.choice(available_classes)
                current_class_counts[selected_class] += 1
                schedule[day][hour] = selected_class

        population.append(schedule)

    return population


# Obliczanie dopasowania dla planu zajęć
def calculate_fitness(schedule):
    conflicts = 0
    empty_count = 0  # Licznik pustych zajęć

    for day in range(len(days)):
        for hour in range(len(hours)):
            class1 = schedule[day][hour]
            if class1 == "":
                empty_count += 1

            for other_day in range(len(days)):
                for other_hour in range(len(hours)):
                    if (day != other_day or hour != other_hour) and class1 == schedule[other_day][other_hour]:
                        conflicts += 1

            # Sprawdzanie, czy zajęcia nie naruszają ograniczeń
            if class1 in preferences:
                if day not in preferences[class1][0] or hour not in preferences[class1][1]:
                    conflicts += 1

    # Obliczanie dopasowania, uwzględniając zarówno konflikty, jak i liczbę pustych zajęć
    fitness = 1 / (conflicts + 1)
    empty_penalty = 1 / (empty_count + 1)
    return fitness + empty_penalty

# Selekcja osobników
# Selekcja osobników
def selection(population):
    fitness_scores = [calculate_fitness(schedule) for schedule in population]
    selected_population = []

    # Elitarność - wybierz najlepsze rozwiązanie bez zmian
    best_schedule = max(population, key=calculate_fitness, default=None)
    selected_population.append(best_schedule)

    # Selekcja turniejowa
    tournament_size = min(5, len(population))
    while len(selected_population) < population_size:
        participants = random.sample(population, tournament_size)
        winner = max(participants, key=calculate_fitness)
        selected_population.append(winner)

    return selected_population

# Krzyżowanie osobników
def crossover(parent1, parent2):
    child = np.copy(parent1)
    for day in range(len(days)):
        for hour in range(len(hours)):
            if child[day][hour] != parent2[day][hour]:
                if random.random() < crossover_rate:
                    child[day][hour] = parent2[day][hour]
    return child

# Mutacja osobników
def mutate(schedule):
    for _ in range(len(days) * len(hours)):
        if random.random() < mutation_rate:
            day1 = random.randint(0, len(days) - 1)
            hour1 = random.randint(0, len(hours) - 1)
            day2 = random.randint(0, len(days) - 1)
            hour2 = random.randint(0, len(hours) - 1)

            # Swap classes between two randomly selected positions
            schedule[day1][hour1], schedule[day2][hour2] = schedule[day2][hour2], schedule[day1][hour1]

    return schedule


# Algorytm genetyczny
def genetic_algorithm():
    population = generate_initial_population()

    for _ in range(generations):
        population = selection(population)

        next_generation = []

        while len(next_generation) < population_size:
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_generation.append(child)

        population = next_generation

    best_schedule = max(population, key=calculate_fitness)
    return best_schedule

def import_constraints():
    global preferences
    constraints = {
        "Matematyka": (["Poniedziałek"], ["8:00-9:30", "9:45-11:15", "11:30-13:00"]),
        "Historia": (["Wtorek", "Środa", "Czwartek"], ["9:45-11:15", "11:30-13:00"]),
        "Język angielski": (["Poniedziałek", "Środa", "Piątek"], ["9:45-11:15"]),
        "Fizyka": (["Poniedziałek", "Wtorek", "Czwartek"], ["8:00-9:30", "11:30-13:00"]),
        "Biologia": (["Wtorek", "Czwartek"], ["9:45-11:15"]),
        "Chemia": (["Poniedziałek", "Piątek"], ["8:00-9:30"]),
        "Wychowanie fizyczne": (["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"], ["8:00-9:30", "9:45-11:15", "11:30-13:00", "14:00-15:30"])
    }

    for subject, hours_days in constraints.items():
        selected_hours, selected_days = hours_days
        preferences[subject] = (selected_days, selected_hours)

    preferences = constraints

    messagebox.showinfo("Import ograniczeń", "Ograniczenia zostały zaimportowane pomyślnie.")
    display_preferences()  # Wyświetlanie zaimportowanych ograniczeń po aktualizacji

# Tworzenie interfejsu graficznego

tk.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Tworzenie głównego okna aplikacji
root = tk.CTk()
root.title("Generator planu zajęć")

# Wybór preferencji zajęć
preferences_frame = tk.CTkFrame(master=root)
preferences_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Kontener na plan zajęć
schedule_frame = tk.CTkFrame(root)
schedule_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Etykieta i lista rozwijana dla wyboru przedmiotu
subject_label = tk.CTkLabel(preferences_frame, text="Przedmiot:")
subject_label.grid(row=0, column=0, padx=5, pady=5)
subject_var = tk.StringVar(value="Przedmiot")
subject_dropdown = tk.CTkOptionMenu(master=preferences_frame, values=classes, variable=subject_var)
subject_dropdown.grid(row=0, column=1, padx=5, pady=5)

# Lista dni tygodnia
days_label = tk.CTkLabel(preferences_frame, text="Dni:")
days_label.grid(row=1, column=0, padx=5, pady=5)
days_vars = [tk.IntVar() for _ in range(len(days))]
for i, day in enumerate(days):
    day_checkbox = tk.CTkCheckBox(preferences_frame, text=day, variable=days_vars[i])
    day_checkbox.grid(row=1, column=i + 1, padx=2, pady=2)

# Lista godzin
hours_label = tk.CTkLabel(preferences_frame, text="Godziny:")
hours_label.grid(row=2, column=0, padx=5, pady=5)
hours_vars = [tk.IntVar() for _ in range(len(hours))]
for i, hour in enumerate(hours):
    hour_checkbox = tk.CTkCheckBox(preferences_frame, text=hour, variable=hours_vars[i])
    hour_checkbox.grid(row=2, column=i + 1, padx=2, pady=2)

# Przycisk do dodawania preferencji
add_button = tk.CTkButton(preferences_frame, text="Dodaj preferencje", command=add_preferences)
add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=15)

# Przycisk do usuwania preferencji
remove_button = tk.CTkButton(preferences_frame, text="Usuń preferencję", command=remove_preference)
remove_button.grid(row=3, column=2, columnspan=2, padx=5, pady=15)

# Przycisk do usuwania wszystkich preferencji
remove_all_button = tk.CTkButton(preferences_frame, text="Usuń wszystkie preferencje", command=remove_all_preferences)
remove_all_button.grid(row=3, column=4, columnspan=2, padx=5, pady=15)

# Pole tekstowe z wyświetlonymi preferencjami
style = ttk.Style()

preferences_tree = tkinter.ttk.Treeview(preferences_frame, columns=("Przedmiot", "Dni", "Godziny"), show="headings", style="Treeview")
style.theme_use("vista")
style.map("Treeview", background=[("selected", "#1f538d")])

preferences_tree.heading("Przedmiot", text="Przedmiot")
preferences_tree.heading("Dni", text="Dni")
preferences_tree.heading("Godziny", text="Godziny")
preferences_tree.column("Przedmiot", width=10, anchor=tk.CENTER, stretch=True)
preferences_tree.column("Dni", width=100, anchor=tk.CENTER, stretch=True)
preferences_tree.column("Godziny", width=200, anchor=tk.CENTER, stretch=True)
preferences_tree.grid(row=4, column=0, columnspan=8, padx=5, pady=5, sticky="nsew")

preferences_frame.columnconfigure(0, weight=1)
preferences_frame.rowconfigure(4, weight=1)

# Etykiety dla parametrów algorytmu genetycznego
param_labels_frame = tk.CTkFrame(root, bg_color="#1a1a1a")
param_labels_frame.pack(pady=10)

pop_size_label = tk.CTkLabel(param_labels_frame, text="Rozmiar populacji:")
pop_size_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

gen_label = tk.CTkLabel(param_labels_frame, text="Liczba generacji:")
gen_label.grid(row=0, column=2, columnspan=2, padx=5, pady=5)

mut_rate_label = tk.CTkLabel(param_labels_frame, text="Współczynnik mutacji:")
mut_rate_label.grid(row=0, column=4, columnspan=2, padx=5, pady=5)

cross_rate_label = tk.CTkLabel(param_labels_frame, text="Współczynnik krzyżowania:")
cross_rate_label.grid(row=0, column=6, columnspan=2, padx=5, pady=5)


# Pola tekstowe dla parametrów algorytmu genetycznego
param_entries_frame = tk.CTkFrame(root)
param_entries_frame.pack(pady=10)

population_size_entry = tk.CTkEntry(param_labels_frame, width=50)
population_size_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
population_size_entry.insert(0, 50)

generations_entry = tk.CTkEntry(param_labels_frame, width=50)
generations_entry.grid(row=1, column=2, columnspan=2, padx=5, pady=5)
generations_entry.insert(0, 10)

mutation_rate_entry = tk.CTkEntry(param_labels_frame, width=50)
mutation_rate_entry.grid(row=1, column=4, columnspan=2, padx=5, pady=5)
mutation_rate_entry.insert(0, str(mutation_rate))

crossover_rate_entry = tk.CTkEntry(param_labels_frame, width=50)
crossover_rate_entry.grid(row=1, column=6, columnspan=2, padx=5, pady=5)
crossover_rate_entry.insert(0, str(crossover_rate))



# Kontener na przyciski i pola tekstowe
# buttons_frame = tk.CTkFrame(root)
# buttons_frame.pack(pady=10)





# Przycisk do generowania planu zajęć
generate_button = tk.CTkButton(param_labels_frame, text="Generuj plan zajęć", command=generate_schedule)
generate_button.grid(row=2, column=2, columnspan=2, padx=5, pady=15)

# Przycisk do importowania ograniczeń
import_button = tk.CTkButton(param_labels_frame, text="Importuj ograniczenia", command=import_constraints)
import_button.grid(row=2, column=4, columnspan=2, padx=5, pady=15)

# Przycisk powrotu
# return_button = tk.CTkButton(root, text="Powrót", command=return_to_preferences)
# return_button.pack_forget()  # Ukrycie przycisku powrotu na początku

root.mainloop()
