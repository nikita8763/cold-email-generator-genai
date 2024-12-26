import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Cold Mail Generator"

chain = Chain()
portfolio = Portfolio()

app.layout = dbc.Container(
    [
        html.H1("📧 Cold Mail Generator", className="text-center my-4"),
        
        html.H5("Enter the URL of the Job Posting:", className="mt-10 pt-9"),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Input(
                            id="url-input",
                            placeholder="Enter a URL",
                            value="https://jobs.nike.com/job/R-46057?from=job%20search%20funnel",
                            type="url",
                            className="mb-3",
                            style={"padding": "12px", "font-size": "1rem"}
                        ),
                        dbc.Button(
                            "Submit",
                            id="submit-button",
                            color="primary",
                            className="mb-3",
                            style={"padding": "12px 24px", "font-size": "1rem"}
                        ),
                        html.Div(id="error-message", className="text-danger", style={"padding-top": "10px"}),
                    ],
                    width=12, 
                    className="mb-4",  
                ),
            ],
            justify="center", 
        ),

        dbc.Row(
            dbc.Col(
                html.Div(id="email-output", className="mt-4", style={"padding": "20px", "border": "1px solid #ccc", "border-radius": "8px", "background-color": "#f9f9f9"}),
                width=12,  
            ),
            justify="center", 
        ),
    ],
    fluid=True,
    style={"padding": "20px", "padding-left": "40px", "padding-right": "40px"},  
)

@app.callback(
    [Output("email-output", "children"), Output("error-message", "children")],
    [Input("submit-button", "n_clicks")],
    [State("url-input", "value")],
)
def generate_email(n_clicks, url_input):
    if not n_clicks:
        return "", ""

    try:
        loader = WebBaseLoader([url_input])
        loaded_data = loader.load()

        if isinstance(loaded_data, list) and len(loaded_data) > 0:
            data = clean_text(loaded_data[0].page_content)  
        else:
            raise ValueError("Loaded data is empty or not in the expected format.")

        portfolio.load_portfolio()
        jobs = chain.extract_jobs(data)

        emails = []
        for job in jobs:
            skills = job.get("skills", [])
            skills_string = ", ".join(skills)
            links = portfolio.query_links(skills_string)
            email = chain.write_mail(job, links)
            emails.append(html.Pre(email, style={"whiteSpace": "pre-wrap", "wordWrap": "break-word"}))

        return emails, ""

    except Exception as e:
        return "", f"An Error Occurred: {e}"


if __name__ == "__main__":
    app.run_server(debug=True)
