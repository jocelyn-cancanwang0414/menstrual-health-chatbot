"""
Cycle Calculator - Calculate cycle day and phase based on last period date and cycle length.
"""

from datetime import datetime, date
from typing import Tuple


def calculate_cycle_day_and_phase(last_period_date: date, cycle_length: int = 28, current_date: date = None) -> Tuple[int, str, str]:
    """
    Calculate the current cycle day and phase based on the last period date.
    
    Args:
        last_period_date: The date of the last period start (date object)
        cycle_length: The typical length of the menstrual cycle in days (default: 28)
        current_date: The date to calculate from (default: today's date)
    
    Returns:
        A tuple containing:
        - cycle_day: Current day in the cycle (1-based)
        - phase: The current phase name
        - phase_description: Description of the phase
    """
    if current_date is None:
        current_date = date.today()
    
    # Calculate days since last period
    days_since_last_period = (current_date - last_period_date).days
    
    # Calculate current cycle day (modulo cycle length to handle multiple cycles)
    cycle_day = (days_since_last_period % cycle_length) + 1
    
    # If we're before the next expected period, use the current cycle
    # Otherwise, we've already had the next period, so adjust
    if days_since_last_period < 0:
        # Future date, return error or handle appropriately
        return -1, "Invalid", "Current date is before last period date"
    
    # Determine phase based on cycle day
    if 1 <= cycle_day <= 7:
        phase = "Menstrual Phase"
        phase_description = "The start of your cycle, when you bleed. Low energy, potential cramps, need for rest/gentle exercise (yoga, walking)."
    elif 8 <= cycle_day <= 13:
        phase = "Follicular Phase"
        phase_description = "Hormones build, follicles (eggs) mature, uterine lining thickens. Rising energy, focus, confidence; good for goal-setting."
    elif 14 <= cycle_day <= 15:
        phase = "Ovulatory Phase"
        phase_description = "An ovary releases an egg (ovulation). Energy peaks, libido increases, potential for mild pain, increased cervical fluid (egg-white consistency)."
    else:  # 16 <= cycle_day <= cycle_length
        phase = "Luteal Phase"
        phase_description = "Body prepares for pregnancy; progesterone rises, then drops if no pregnancy. PMS symptoms (bloating, mood swings, cravings, fatigue) as hormones drop."
    
    return cycle_day, phase


def get_phase_info(cycle_day: int) -> Tuple[str, str]:
    """
    Get phase information for a given cycle day.
    
    Args:
        cycle_day: The day in the cycle (1-based)
    
    Returns:
        A tuple containing (phase_name, phase_description)
    """
    if 1 <= cycle_day <= 7:
        return "Menstrual Phase", "The start of your cycle, when you bleed. Low energy, potential cramps, need for rest/gentle exercise (yoga, walking)."
    elif 8 <= cycle_day <= 13:
        return "Follicular Phase", "Hormones build, follicles (eggs) mature, uterine lining thickens. Rising energy, focus, confidence; good for goal-setting."
    elif 14 <= cycle_day <= 15:
        return "Ovulatory Phase", "An ovary releases an egg (ovulation). Energy peaks, libido increases, potential for mild pain, increased cervical fluid (egg-white consistency)."
    else:
        return "Luteal Phase", "Body prepares for pregnancy; progesterone rises, then drops if no pregnancy. PMS symptoms (bloating, mood swings, cravings, fatigue) as hormones drop."


def main():
    """Example usage of the cycle calculator."""
    # Example: Last period was 10 days ago, with a 28-day cycle
    last_period = date.today() - date.resolution * 10
    cycle_length = 28
    
    cycle_day, phase, description = calculate_cycle_day_and_phase(last_period, cycle_length)
    
    print(f"Last Period Date: {last_period}")
    print(f"Cycle Length: {cycle_length} days")
    print(f"Current Cycle Day: {cycle_day}")
    print(f"Current Phase: {phase}")
    print(f"Phase Description: {description}")


if __name__ == "__main__":
    main()
