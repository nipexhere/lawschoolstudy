def get_student_name():
    """Return a non-empty student name."""
    while True:
        name = input("Enter student's name: ").strip()
        if name:
            return name
        print("Name cannot be empty. Please try again.")


def get_scores():
    """Collect one or more scores between 0 and 100."""
    scores = []
    print("Enter scores one at a time. Enter 'done' when finished.")

    while True:
        value = input(f"Enter score {len(scores) + 1}: ").strip()
        if value.lower() == "done":
            if scores:
                return scores
            print("Enter at least one score before finishing.")
            continue

        try:
            score = float(value)
        except ValueError:
            print("Please enter a number from 0 to 100, or 'done'.")
            continue

        if not 0 <= score <= 100:
            print("Score must be between 0 and 100.")
            continue
        scores.append(score)


def calculate_average(scores):
    """Return the arithmetic mean of the scores."""
    if not scores:
        raise ValueError("At least one score is required.")
    return sum(scores) / len(scores)


def calculate_grade(average):
    """Return a letter grade for an average score."""
    if average >= 90:
        return "A"
    if average >= 80:
        return "B"
    if average >= 70:
        return "C"
    if average >= 60:
        return "D"
    return "F"


def display_result(name, scores, average, grade):
    """Display a student's scores and result."""
    formatted_scores = ", ".join(f"{score:g}" for score in scores)
    print("\nStudent Result")
    print("--------------")
    print(f"Name: {name}")
    print(f"Scores: {formatted_scores}")
    print(f"Average: {average:.2f}")
    print(f"Grade: {grade}")


def main():
    """Run the Student Score Manager."""
    name = get_student_name()
    scores = get_scores()
    average = calculate_average(scores)
    grade = calculate_grade(average)
    display_result(name, scores, average, grade)


if __name__ == "__main__":
    main()