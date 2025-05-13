#!/usr/bin/env python3
import pandas as pd
import random

def generate_boxing_data(boxer_a_name="Boxer A", boxer_b_name="Boxer B", num_rounds=12):
    """Generates sample round-by-round boxing match data."""
    data = []
    for round_num in range(1, num_rounds + 1):
        for boxer, opponent in [(boxer_a_name, boxer_b_name), (boxer_b_name, boxer_a_name)]:
            # Simulate punches
            punches_thrown = random.randint(40, 80)
            punches_landed = random.randint(int(punches_thrown * 0.2), int(punches_thrown * 0.5))
            
            sig_punches_thrown = random.randint(int(punches_thrown * 0.4), int(punches_thrown * 0.7))
            sig_punches_landed = random.randint(int(punches_landed * 0.5), punches_landed)
            if sig_punches_landed > sig_punches_thrown:
                 sig_punches_landed = sig_punches_thrown # Landed cannot exceed thrown
            if sig_punches_landed < int(sig_punches_thrown * 0.1):
                 sig_punches_landed = int(sig_punches_thrown * 0.1) # Ensure some minimum landing rate

            # Break down significant punches
            head_landed = random.randint(int(sig_punches_landed * 0.4), int(sig_punches_landed * 0.8))
            body_landed = sig_punches_landed - head_landed

            # Jabs vs Power punches (assuming power punches are the significant ones)
            power_punches_landed = sig_punches_landed
            jabs_landed = punches_landed - power_punches_landed
            if jabs_landed < 0:
                jabs_landed = 0 # Jabs can't be negative
                power_punches_landed = punches_landed # Adjust if calculation was off

            # Simulate ring control (percentage)
            ring_control_pct = random.uniform(30.0, 70.0)

            data.append({
                "Round": round_num,
                "Boxer": boxer,
                "Opponent": opponent,
                "Punches Thrown": punches_thrown,
                "Punches Landed": punches_landed,
                "Significant Punches Thrown": sig_punches_thrown,
                "Significant Punches Landed": sig_punches_landed,
                "Head Punches Landed": head_landed,
                "Body Punches Landed": body_landed,
                "Jabs Landed": jabs_landed,
                "Power Punches Landed": power_punches_landed,
                "Ring Control %": round(ring_control_pct, 1)
            })

    df = pd.DataFrame(data)
    
    # Ensure ring control for both boxers sums to 100% per round
    for round_num in range(1, num_rounds + 1):
        boxer_a_idx = df[(df['Round'] == round_num) & (df['Boxer'] == boxer_a_name)].index
        boxer_b_idx = df[(df['Round'] == round_num) & (df['Boxer'] == boxer_b_name)].index
        
        if not boxer_a_idx.empty and not boxer_b_idx.empty:
            a_control = df.loc[boxer_a_idx[0], 'Ring Control %']
            # Adjust B's control to make it sum to 100
            df.loc[boxer_b_idx[0], 'Ring Control %'] = 100.0 - a_control
            
    return df

if __name__ == "__main__":
    match_data = generate_boxing_data(boxer_a_name="Lightning Lewis", boxer_b_name="Thunder Thompson")
    match_data.to_csv("boxing_match_data.csv", index=False)
    print("Sample boxing match data generated and saved to boxing_match_data.csv")

