from psychopy import core, visual, event, gui
import random
import csv
import os

# Setup participant dialog box to get basic info and condition assignment
exp_info = {'Participant': ''}
dlg = gui.DlgFromDict(exp_info, title="Cognitive Psych Experiment")
if not dlg.OK:
    core.quit()

# Get the current directory and create the filename with participant number
current_directory = os.getcwd()
filename = os.path.join(current_directory, f"participant_{exp_info['Participant']}_results.csv")

# Randomly assign participant to either 3-second or infinite time condition
condition = random.choice([3, None])  # 3 seconds or infinite time
exp_info['Condition'] = f"{condition if condition else 'infinite'} seconds"

# Setup experiment window with black background and white text
win = visual.Window([800, 600], color="black", fullscr=False)

# Predefined list of math questions and correct answers
question_bank = [
    "What is 5 + 3: 8",
    "What is 10 - 4: 6",
    "What is 7 * 2: 14",
    "What is 20 / 4: 5",
    "What is 15 + 7: 22",
    "What is 9 - 3: 6",
    "What is 8 * 2: 16",
    "What is 12 / 3: 4",
    "What is 6 + 9: 15",
    "What is 8 - 3: 5"
]

questions = [qa.split(': ')[0] for qa in question_bank]
answers = [int(qa.split(': ')[1]) for qa in question_bank]

# Instruction screen
instruction = visual.TextStim(
    win, 
    text="Please type your answer and press enter to submit. Press the spacebar to start.",
    color="white"
)
instruction.draw()
win.flip()
event.waitKeys(keyList=['space'])

correct_answers = 0
trial_count = len(questions)
all_responses = []

# Shuffle the questions and answers
paired_questions = list(zip(questions, answers))
random.shuffle(paired_questions)

for trial in range(trial_count):
    question_text, correct_answer = paired_questions[trial]
    question_stim = visual.TextStim(win, text=question_text, color="white", pos=(0, 0.3))

    answer_box = visual.TextBox2(
        win, 
        text='', 
        font='Arial',
        pos=(0, -0.2), 
        letterHeight=0.05, 
        color='white', 
        borderColor='white',
        size=(0.3, 0.1)
    )
    
    timer_text = visual.TextStim(win, text=f"Time: {condition if condition else '∞'}", color="white", pos=(0.4, 0.4))
    question_stim.draw()
    answer_box.draw()
    timer_text.draw()
    win.flip()

    response_timer = core.Clock()
    answer_given = False
    response_text = ''
    
    while not answer_given:
        if condition and response_timer.getTime() >= condition:
            break  # Stop after 3 seconds
        if condition is None and not answer_given:  # Infinite time condition
            remaining_time = "∞"
        else:
            remaining_time = max(0, int(condition - response_timer.getTime())) if condition else "∞"
        
        # Update the timer text
        timer_text.text = f"Time: {remaining_time}"
        question_stim.draw()
        answer_box.draw()
        timer_text.draw()
        win.flip()

        keys = event.getKeys()
        for key in keys:
            if key in ['return', 'num_enter']:  # Check for enter key
                all_responses.append({
                    'trial': trial + 1,
                    'condition': f"{condition if condition else 'infinite'} seconds",  # Log the condition for each trial
                    'question': question_text,
                    'response': response_text,
                    'correct_answer': correct_answer,
                    'is_correct': response_text == str(correct_answer)  # Compare as strings
                })
                
                if response_text == str(correct_answer):  # Check correctness
                    correct_answers += 1
                
                answer_given = True
                break
            elif key == 'backspace':
                response_text = response_text[:-1]  # Remove last character
            elif key == 'space':
                response_text += ' '  # Add space if space bar is pressed
            else:
                # If the key starts with "num_", strip that part and log just the number
                if key.startswith("num_"):
                    response_text += key[-1]  # Append the last character (the number itself)
                else:
                    response_text += key  # Add any other character directly to the response_text

            # Update the answer box with the current response
            answer_box.text = response_text
            question_stim.draw()
            answer_box.draw()
            timer_text.draw()
            win.flip()

# End screen message
results_text = f"Press the spacebar to exit."
result_screen = visual.TextStim(win, text=results_text, color="white")
result_screen.draw()
win.flip()
event.waitKeys(keyList=['space'])

# Write results to a CSV file
with open(filename, 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['trial', 'condition', 'question', 'response', 'correct_answer', 'is_correct'])
    writer.writeheader()
    writer.writerows(all_responses)

print(f"Results saved to {filename}")

win.close()
core.quit()
