Streamlit frontend

Run locally:

1. Install dependencies:

```bash
python -m pip install -r requirements-streamlit.txt
```

2. Run the app:

```bash
streamlit run streamlit_app.py
```

3. By default the app expects backend at `http://localhost:8000`. To change, set Streamlit secret `backend_url` or modify `BACKEND` in `streamlit_app.py`.

Notes:

- Login uses `/auth/login` OAuth2 form and stores JWT in session state.
- Network view calls `/connections/user/{id}` to render the graph.
- Profile page fetches `/users/{id}` and allows simple updates with PUT.
