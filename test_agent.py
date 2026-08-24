def calculate_budget(days, daily_cost):
    return days * daily_cost

if __name__ == "__main__":
    total = calculate_budget(5, 150)
    print(f"Total Travel Budget: ${total}")