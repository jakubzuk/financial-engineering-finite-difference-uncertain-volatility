import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Dane historyczne dla indeksu WIG20 - właściwie niepotrzebne, ale można porównać
df = pd.read_csv('wig20_d.csv')
df["Data"] = pd.to_datetime(df["Data"])
df = df[(df["Data"] >= "2021-01-01") & (df["Data"] <= "2025-12-31")]

# Parametry symulacji
# S_0 = df["Zamkniecie"].iloc[-1]
S_0 = 3200
print(f"Obecna cena WIG20 (S0): {S_0:.2f}")
T = 1.0 # czas do wygaśnięcia opcji w latach
# dt = T / (365 * 1)
dt = 1 / 10000

sigma_l = 0.2   # Przedział zmienności
sigma_h = 0.3

# r = 0.0324 # stopa wolna od ryzyka
r = 0.05
N = 30000 # liczba symulacji
seed = 42

# Parametry opcji
K       = 3200    # strike
B_call  = 3600    # bariera Call
B_put   = 2800    # bariera Put 

np.random.seed(seed)

def simulate_paths(S_0, T, dt, sigma_l, sigma_h, r, N):
    M = int(T / dt)  # liczba kroków czasowych
    sigma = sigma_l
    drift = (r - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt)

    # N_half = N // 2
    # Z = np.random.standard_normal((N_half, M))
    # increments_pos = drift + diffusion * Z
    # increments_neg = drift + diffusion * (-Z)
    # increments = np.concatenate([increments_pos, increments_neg], axis=0)

    Z = np.random.standard_normal((N, M))
    increments = drift + diffusion * Z
    log_paths = np.cumsum(increments, axis=1)
    log_paths = np.insert(log_paths, 0, 0, axis=1)
    paths = S_0 * np.exp(log_paths)

    return paths

paths = simulate_paths(S_0, T, dt, sigma_l, sigma_h, r, N)


# paths_to_plot = paths[:50, :]

# time_axis = np.linspace(0, T, paths.shape[1])

# plt.figure(figsize=(12, 7))
# plt.plot(time_axis, paths_to_plot.T, color='lightblue', alpha=0.5)

# plt.axhline(y=S_0, color='black', linestyle='--', label=f'Cena startowa S0 = {S_0:.2f}')
# plt.axhline(y=K, color='green', linestyle='--', label=f'Strike K = {K}')
# plt.axhline(y=B_call, color='red', linestyle='-', label=f'Bariera CALL Up-and-Out = {B_call}')
# plt.axhline(y=B_put, color='darkorange', linestyle='-', label=f'Bariera PUT = {B_put}') 

# plt.title(f'Symulacja {len(paths_to_plot)} ścieżek WIG20 metodą Monte Carlo', fontsize=15)
# plt.xlabel('Czas (w latach)', fontsize=12)
# plt.ylabel('Cena WIG20', fontsize=12)
# plt.legend()
# plt.grid(True, alpha=0.3)

# plt.show()

def price_european_call_knockout(paths, K, B_call):

    barrier_hit = np.any(paths >= B_call, axis=1)

    survived = (barrier_hit == False)

    S_T = paths[:, -1]
    payoff = np.maximum(S_T - K, 0) * survived

    discount = np.exp(-r * T)
    price = discount * np.mean(payoff)

    return price

print(f"Cena opcji europejskiej CALL z barierą: {price_european_call_knockout(paths, K, B_call):.2f}")  

# results = []
# for S in range(1000, 3551, 10):
#     # pass
#     results.append((S, price_european_call_knockout(simulate_paths(S, T, dt, sigma_l, sigma_h, r, N), K, B_call)))

# results_df = pd.DataFrame(results, columns=['S0', 'Call_Price'])
# plt.figure(figsize=(10, 6))
# plt.plot(results_df['S0'], results_df['Call_Price'], marker='o', linestyle='-', color='blue')
# plt.title('Cena opcji europejskiej CALL z barierą w zależności od ceny startowej S0', fontsize=14)
# plt.xlabel('Cena startowa S0', fontsize=12)
# plt.ylabel('Cena opcji CALL', fontsize=12)
# plt.grid(True, alpha=0.3)
# plt.show()