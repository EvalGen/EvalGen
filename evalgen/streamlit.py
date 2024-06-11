import streamlit as st

from evalgen.evals import LLMAssistedEval
from evalgen.llm import invoke
from evalgen.prompts import (
    generate_assertions as generate_assertions_prompt,
    generate_criteria as generate_criteria_prompt,
)


def generate_criteria(prompt):
    response = invoke(
        [
            {"role": "system", "content": generate_criteria_prompt.system.render()},
            {
                "role": "user",
                "content": generate_criteria_prompt.user.render(prompt=prompt),
            },
        ]
    )

    criteria = [
        criterion.split(". ", 1)[1].strip() for criterion in response.split("\n")
    ]

    return criteria


async def generate_assertions(criterion):
    response = invoke(
        [
            {"role": "system", "content": generate_assertions_prompt.system.render()},
            {
                "role": "user",
                "content": generate_assertions_prompt.user.render(criterion=criterion),
            },
        ]
    )

    print(response)

    return [
        assertion.split(". ", 1)[1].strip()
        for assertion in response.split("\n")
        if assertion
    ]


def evaluate_response(evaluation, response, local_context):
    return evaluation.eval("", response)


"""
Generate an article for the following topic:
{topic}
"""


# Initialize session state to keep track of criteria and assertions
if "criteria" not in st.session_state:
    st.session_state.criteria = []
if "assertions" not in st.session_state:
    st.session_state.assertions = []


# Function to reset session state
def reset_session():
    st.session_state.criteria = []
    st.session_state.assertions = []


# Streamlit UI
st.title("EvalGen Prototype")

# Step 1: Prompt Input
st.header("Step 1: Enter your prompt")
prompt = st.text_area("Enter your prompt:", "Your prompt text here", key="prompt_input")

# Step 2: Generate Criteria
if st.button("Generate Criteria"):
    st.session_state.criteria = generate_criteria(prompt)

# Display Generated Criteria
if st.session_state.criteria:
    st.subheader("Generated Criteria")
    for criterion in st.session_state.criteria:
        st.write(f"- **Criterion:** {criterion}")
    st.write("---")

    # Step 3: Generate Assertions
    if st.button("Generate Assertions"):
        st.session_state.assertions = [
            generate_assertions(criterion) for criterion in st.session_state.criteria
        ]

# Display Generated Assertions
if st.session_state.assertions:
    st.subheader("Generated Assertions")
    for criterion, assertions in zip(
        st.session_state.criteria, st.session_state.assertions
    ):
        st.write(f"**Criterion:** {criterion}")
        st.write("**Candidate Assertions:**")
        for assertion in assertions:
            st.write(f"    - {assertion}")
        st.write("---")

    # Placeholder for LLM output and grading
    st.header("Step 4: Grade the LLM Output")
    llm_output = st.text_area("LLM Output:", "Sample LLM output", key="llm_output")
    grade = st.radio("Is this response Good or Bad?", ("Good", "Bad"))
    st.write("Your Grade:", grade)

    # Evaluate the response
    evaluations = {}
    for criterion, assertions in zip(
        st.session_state.criteria, st.session_state.assertions
    ):
        evaluations[criterion] = [
            LLMAssistedEval(
                name=criterion,
                description=criterion,
                assertion=assertion,
            )
            for assertion in assertions
        ]

    st.subheader("Evaluation Results")
    for criterion, evals in evaluations.items():
        st.write(f"Evaluation for '{criterion}':")
        for evaluation in evals:
            result = evaluation.eval("", llm_output)

# Reset Button
if st.button("Reset"):
    reset_session()
