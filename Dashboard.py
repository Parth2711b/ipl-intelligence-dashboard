# dashboard.py
# Run this file with: python dashboard.py
# Then open browser: http://localhost:8050

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, dash_table
import os

# ── Load Data ─────────────────────────────────────────────────
base = r"D:\COEP\Cricket_Project\data\processed"

df            = pd.read_csv(f"{base}\\ipl_cleaned.csv", parse_dates=['start_date'])
season_stats  = pd.read_csv(f"{base}\\season_stats.csv")
venue_stats   = pd.read_csv(f"{base}\\venue_stats.csv")
team_stats    = pd.read_csv(f"{base}\\team_stats.csv")
bowl_compare  = pd.read_csv(f"{base}\\bowling_stats.csv")
h2h           = pd.read_csv(f"{base}\\h2h_stats.csv")
batting_stats = pd.read_csv(f"{base}\\batting_stats.csv")

# Filter qualified players
batting_qualified = batting_stats[batting_stats['innings'] >= 20].copy()
bowling_qualified = bowl_compare.copy()

# ── App Init ──────────────────────────────────────────────────
app = Dash(__name__)
app.title = "IPL Intelligence Dashboard"

# ── Colors ───────────────────────────────────────────────────
COLORS = {
    'bg':       '#0f1117',
    'card':     '#1a1d27',
    'accent':   '#E8612C',
    'blue':     '#3498db',
    'green':    '#2ecc71',
    'text':     '#ffffff',
    'subtext':  '#8892a4',
    'border':   '#2d3140',
}

TEAM_COLORS = {
    'Chennai Super Kings':        '#F9CD05',
    'Mumbai Indians':             '#004BA0',
    'Kolkata Knight Riders':      '#3A225D',
    'Royal Challengers Bangalore':'#EC1C24',
    'Rajasthan Royals':           '#EA1A85',
    'Delhi Capitals':             '#0078BC',
    'Sunrisers Hyderabad':        '#FF822A',
    'Punjab Kings':               '#ED1B24',
    'Gujarat Titans':             '#1D4DB5',
    'Lucknow Super Giants':       '#A4DE02',
}

# ── Layout ────────────────────────────────────────────────────
app.layout = html.Div(style={'backgroundColor': COLORS['bg'],
                              'minHeight': '100vh',
                              'fontFamily': 'Inter, sans-serif',
                              'color': COLORS['text']}, children=[

    # Header
    html.Div(style={'background': 'linear-gradient(135deg, #E8612C, #c0392b)',
                    'padding': '24px 40px',
                    'marginBottom': '24px'}, children=[
        html.H1("IPL Intelligence Dashboard",
                style={'margin': 0, 'fontSize': '28px', 'fontWeight': '700'}),
        html.P("Context-aware cricket analytics — beyond traditional stats",
               style={'margin': '4px 0 0', 'opacity': '0.85', 'fontSize': '14px'})
    ]),

    # Tabs
    dcc.Tabs(id='tabs', value='tab-overview',
             style={'backgroundColor': COLORS['bg']},
             colors={'border': COLORS['border'],
                     'primary': COLORS['accent'],
                     'background': COLORS['card']},
             children=[

        # ── TAB 1: IPL Overview ──────────────────────────────
        dcc.Tab(label='IPL Overview', value='tab-overview',
                style={'color': COLORS['subtext']},
                selected_style={'color': COLORS['text'],
                                'backgroundColor': COLORS['card']},
                children=[
            html.Div(style={'padding': '24px'}, children=[

                html.H3("How IPL has evolved over the years",
                        style={'marginBottom': '16px'}),

                dcc.Graph(id='season-evolution'),

                html.Div(style={'display': 'grid',
                                'gridTemplateColumns': '1fr 1fr',
                                'gap': '20px',
                                'marginTop': '20px'}, children=[
                    dcc.Graph(id='phase-scoring'),
                    dcc.Graph(id='team-winrate'),
                ])
            ])
        ]),

        # ── TAB 2: Player Analysis ───────────────────────────
        dcc.Tab(label='Player Analysis', value='tab-players',
                style={'color': COLORS['subtext']},
                selected_style={'color': COLORS['text'],
                                'backgroundColor': COLORS['card']},
                children=[
            html.Div(style={'padding': '24px'}, children=[

                html.Div(style={'display': 'grid',
                                'gridTemplateColumns': '1fr 1fr',
                                'gap': '20px',
                                'marginBottom': '16px'}, children=[
                    html.Div([
                        html.Label("Select Metric",
                                   style={'color': COLORS['subtext'],
                                          'fontSize': '12px',
                                          'marginBottom': '6px',
                                          'display': 'block'}),
                        dcc.Dropdown(
                            id='batting-metric',
                            options=[
                                {'label': 'Strike Rate',       'value': 'strike_rate'},
                                {'label': 'Batting Average',   'value': 'average'},
                                {'label': 'Total Runs',        'value': 'total_runs'},
                                {'label': 'Boundary Rate %',   'value': 'boundary_rate'},
                                {'label': 'Avg Pressure Faced','value': 'avg_pressure'},
                            ],
                            value='strike_rate',
                            style={'backgroundColor': COLORS['card'],
                                   'color': '#000'}
                        )
                    ]),
                    html.Div([
                        html.Label("Min Innings",
                                   style={'color': COLORS['subtext'],
                                          'fontSize': '12px',
                                          'marginBottom': '6px',
                                          'display': 'block'}),
                        dcc.Slider(id='min-innings',
                                   min=10, max=100, step=10, value=30,
                                   marks={i: str(i) for i in range(10,110,10)})
                    ])
                ]),

                dcc.Graph(id='batting-leaderboard'),
            ])
        ]),

        # ── TAB 3: Venue Analysis ────────────────────────────
        dcc.Tab(label='Venue Analysis', value='tab-venue',
                style={'color': COLORS['subtext']},
                selected_style={'color': COLORS['text'],
                                'backgroundColor': COLORS['card']},
                children=[
            html.Div(style={'padding': '24px'}, children=[
                dcc.Graph(id='venue-bias', style={'height': '600px'}),
            ])
        ]),

        # ── TAB 4: Head to Head ──────────────────────────────
        dcc.Tab(label='Head to Head', value='tab-h2h',
                style={'color': COLORS['subtext']},
                selected_style={'color': COLORS['text'],
                                'backgroundColor': COLORS['card']},
                children=[
            html.Div(style={'padding': '24px'}, children=[

                html.Div(style={'display': 'grid',
                                'gridTemplateColumns': '1fr 1fr',
                                'gap': '20px',
                                'marginBottom': '20px'}, children=[
                    html.Div([
                        html.Label("Select Batter",
                                   style={'color': COLORS['subtext'],
                                          'fontSize':'12px',
                                          'marginBottom':'6px',
                                          'display':'block'}),
                        dcc.Dropdown(
                            id='h2h-batter',
                            options=[{'label': p, 'value': p}
                                     for p in sorted(
                                         h2h[h2h['balls'] >= 20]['striker'].unique())],
                            value='RG Sharma',
                            style={'backgroundColor': COLORS['card'], 'color': '#000'}
                        )
                    ]),
                    html.Div([
                        html.Label("Min Balls in Matchup",
                                   style={'color': COLORS['subtext'],
                                          'fontSize':'12px',
                                          'marginBottom':'6px',
                                          'display':'block'}),
                        dcc.Slider(id='h2h-min-balls',
                                   min=10, max=50, step=5, value=20,
                                   marks={i: str(i) for i in range(10,55,5)})
                    ])
                ]),

                html.Div(style={'display': 'grid',
                                'gridTemplateColumns': '1fr 1fr',
                                'gap': '20px'}, children=[
                    dcc.Graph(id='h2h-best'),
                    dcc.Graph(id='h2h-worst'),
                ])
            ])
        ]),

        # ── TAB 5: Pressure Index ────────────────────────────
        dcc.Tab(label='Pressure Index', value='tab-pressure',
                style={'color': COLORS['subtext']},
                selected_style={'color': COLORS['text'],
                                'backgroundColor': COLORS['card']},
                children=[
            html.Div(style={'padding': '24px'}, children=[
                html.H3("Clutch Performers — Who thrives under pressure?"),
                html.Div(style={'display': 'grid',
                                'gridTemplateColumns': '1fr 1fr',
                                'gap': '20px'}, children=[
                    dcc.Graph(id='pressure-build'),
                    dcc.Graph(id='clutch-batters'),
                ])
            ])
        ]),
    ]),
])

# ── Callbacks ────────────────────────────────────────────────

# Tab 1 — Season evolution
@app.callback(Output('season-evolution','figure'), Input('tabs','value'))
def update_season_evolution(tab):
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Runs Per Match by Season',
                                        'Wickets Per Match by Season'])
    fig.add_trace(go.Scatter(
        x=season_stats['season'], y=season_stats['runs_per_match'],
        mode='lines+markers', name='Runs/Match',
        line=dict(color=COLORS['accent'], width=2.5),
        marker=dict(size=7)), row=1, col=1)

    fig.add_trace(go.Bar(
        x=season_stats['season'], y=season_stats['wickets_per_match'],
        name='Wickets/Match',
        marker_color=COLORS['blue']), row=1, col=2)

    fig.update_layout(paper_bgcolor=COLORS['card'],
                      plot_bgcolor=COLORS['card'],
                      font_color=COLORS['text'],
                      showlegend=False, height=350)
    fig.update_xaxes(gridcolor=COLORS['border'])
    fig.update_yaxes(gridcolor=COLORS['border'])
    return fig

# Tab 1 — Phase scoring
@app.callback(Output('phase-scoring','figure'), Input('tabs','value'))
def update_phase_scoring(tab):
    phase_order = ['Powerplay (0-5)','Middle 1 (6-9)',
                   'Middle 2 (10-14)','Death (15-19)']
    phase_data = df.groupby('phase').agg(
        economy=('total_runs', lambda x:
                 (x.sum() / df.loc[x.index,'is_legal'].sum() * 6))
    ).reset_index() if 'phase' in df.columns else pd.DataFrame()

    if len(phase_data) == 0:
        # Rebuild phase if not in df
        def get_phase(over):
            if over <= 5:   return 'Powerplay (0-5)'
            elif over <= 9: return 'Middle 1 (6-9)'
            elif over <= 14:return 'Middle 2 (10-14)'
            else:           return 'Death (15-19)'
        df['phase'] = df['over_number'].apply(get_phase)
        phase_data = df.groupby('phase').agg(
            total_runs  = ('total_runs','sum'),
            total_balls = ('is_legal','sum')
        ).reset_index()
        phase_data['economy'] = (phase_data['total_runs'] /
                                  phase_data['total_balls'] * 6).round(2)

    phase_data['phase'] = pd.Categorical(
        phase_data['phase'], categories=phase_order, ordered=True)
    phase_data = phase_data.sort_values('phase')

    fig = px.bar(phase_data, x='phase', y='economy',
                 title='Economy by Match Phase',
                 color='economy',
                 color_continuous_scale='RdYlGn_r')
    fig.update_layout(paper_bgcolor=COLORS['card'],
                      plot_bgcolor=COLORS['card'],
                      font_color=COLORS['text'],
                      height=320, showlegend=False)
    fig.update_xaxes(gridcolor=COLORS['border'])
    fig.update_yaxes(gridcolor=COLORS['border'])
    return fig

# Tab 1 — Team win rate
@app.callback(Output('team-winrate','figure'), Input('tabs','value'))
def update_team_winrate(tab):
    major = ['Chennai Super Kings','Mumbai Indians','Kolkata Knight Riders',
             'Royal Challengers Bangalore','Rajasthan Royals','Delhi Capitals',
             'Sunrisers Hyderabad','Punjab Kings','Gujarat Titans',
             'Lucknow Super Giants']
    data  = team_stats[team_stats['team'].isin(major)].sort_values('win_rate')
    colors = [TEAM_COLORS.get(t, COLORS['accent']) for t in data['team']]

    fig = go.Figure(go.Bar(
        x=data['win_rate'], y=data['team'],
        orientation='h',
        marker_color=colors,
        text=[f"{r}%" for r in data['win_rate']],
        textposition='outside'))
    fig.add_vline(x=50, line_dash='dash',
                  line_color='white', opacity=0.4)
    fig.update_layout(paper_bgcolor=COLORS['card'],
                      plot_bgcolor=COLORS['card'],
                      font_color=COLORS['text'],
                      title='Team Win Rates — All Time',
                      height=320, showlegend=False)
    fig.update_xaxes(gridcolor=COLORS['border'])
    fig.update_yaxes(gridcolor=COLORS['gridcolor'] if 'gridcolor' in COLORS else COLORS['border'])
    return fig

# Tab 2 — Batting leaderboard
@app.callback(
    Output('batting-leaderboard','figure'),
    Input('batting-metric','value'),
    Input('min-innings','value')
)
def update_batting_leaderboard(metric, min_innings):
    data = batting_stats[batting_stats['innings'] >= min_innings].nlargest(20, metric)
    metric_labels = {
        'strike_rate':   'Strike Rate',
        'average':       'Batting Average',
        'total_runs':    'Total Runs',
        'boundary_rate': 'Boundary Rate %',
        'avg_pressure':  'Avg Pressure Faced'
    }
    fig = px.bar(data, x=metric, y='striker',
                 orientation='h',
                 title=f'Top 20 Batters by {metric_labels[metric]} (min {min_innings} innings)',
                 color=metric,
                 color_continuous_scale='Viridis',
                 text=metric)
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig.update_layout(paper_bgcolor=COLORS['card'],
                      plot_bgcolor=COLORS['card'],
                      font_color=COLORS['text'],
                      height=600, showlegend=False,
                      yaxis={'categoryorder':'total ascending'})
    fig.update_xaxes(gridcolor=COLORS['border'])
    fig.update_yaxes(gridcolor=COLORS['border'])
    return fig

# Tab 3 — Venue bias
@app.callback(Output('venue-bias','figure'), Input('tabs','value'))
def update_venue_bias(tab):
    data = venue_stats.sort_values('batting_bias', ascending=True)
    colors = ['#E8612C' if b >= 0.6 else
              '#3498db' if b <= 0.4 else
              '#f39c12' for b in data['batting_bias']]

    fig = go.Figure(go.Bar(
        x=data['batting_bias'], y=data['venue'],
        orientation='h',
        marker_color=colors,
        text=[f"{r:.2f}" for r in data['batting_bias']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                      'Batting Bias: %{x:.3f}<br>' +
                      '<extra></extra>'))
    fig.add_vline(x=0.5, line_dash='dash',
                  line_color='white', opacity=0.5,
                  annotation_text='Neutral')
    fig.update_layout(
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card'],
        font_color=COLORS['text'],
        title='Venue Batting Bias Score (Red=Batting | Blue=Bowling)',
        height=580)
    fig.update_xaxes(gridcolor=COLORS['border'])
    fig.update_yaxes(gridcolor=COLORS['border'])
    return fig

# Tab 4 — H2H
@app.callback(
    Output('h2h-best','figure'),
    Output('h2h-worst','figure'),
    Input('h2h-batter','value'),
    Input('h2h-min-balls','value')
)
def update_h2h(batter, min_balls):
    data = h2h[(h2h['striker'] == batter) &
               (h2h['balls'] >= min_balls)].sort_values('batter_dominance',
                                                         ascending=False)
    if len(data) == 0:
        empty = go.Figure()
        empty.update_layout(paper_bgcolor=COLORS['card'],
                             font_color=COLORS['text'],
                             title='No data available')
        return empty, empty

    best  = data.head(10)
    worst = data.tail(10).sort_values('batter_dominance')

    def make_h2h_fig(d, title, color):
        fig = go.Figure(go.Bar(
            x=d['strike_rate'], y=d['bowler'],
            orientation='h', marker_color=color,
            text=[f"SR:{r['strike_rate']} | {r['runs']}R {r['dismissals']}W"
                  for _, r in d.iterrows()],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>SR: %{x}<extra></extra>'))
        fig.update_layout(
            paper_bgcolor=COLORS['card'],
            plot_bgcolor=COLORS['card'],
            font_color=COLORS['text'],
            title=title, height=380,
            xaxis_range=[0, d['strike_rate'].max() * 1.6])
        fig.update_xaxes(gridcolor=COLORS['border'])
        fig.update_yaxes(gridcolor=COLORS['border'],
                         categoryorder='total ascending')
        return fig

    return (make_h2h_fig(best,  f'{batter} — Dominates these bowlers', COLORS['green']),
            make_h2h_fig(worst, f'{batter} — Struggles against these bowlers', COLORS['accent']))

# Tab 5 — Pressure
@app.callback(
    Output('pressure-build','figure'),
    Output('clutch-batters','figure'),
    Input('tabs','value')
)
def update_pressure(tab):
    # Pressure by over
    p_over = df.groupby(['innings','over_number'])['pressure_index'].mean().reset_index()
    fig1 = go.Figure()
    for inn, color, name in [(1, COLORS['blue'],   '1st Innings'),
                              (2, COLORS['accent'], '2nd Innings (Chase)')]:
        d = p_over[p_over['innings'] == inn]
        fig1.add_trace(go.Scatter(
            x=d['over_number'], y=d['pressure_index'],
            mode='lines+markers', name=name,
            line=dict(color=color, width=2.5)))
    fig1.update_layout(
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card'],
        font_color=COLORS['text'],
        title='How Pressure Builds Across Overs',
        height=380)
    fig1.update_xaxes(gridcolor=COLORS['border'])
    fig1.update_yaxes(gridcolor=COLORS['border'])

    # Clutch batters
    high_p = df[df['pressure_index'] > 60].groupby('striker').agg(
        runs=('runs_off_bat','sum'), balls=('is_legal','sum')).reset_index()
    high_p = high_p[high_p['balls'] >= 50]
    high_p['high_sr'] = (high_p['runs'] / high_p['balls'] * 100).round(1)

    low_p = df[df['pressure_index'] < 30].groupby('striker').agg(
        runs=('runs_off_bat','sum'), balls=('is_legal','sum')).reset_index()
    low_p = low_p[low_p['balls'] >= 50]
    low_p['low_sr'] = (low_p['runs'] / low_p['balls'] * 100).round(1)

    merged = high_p[['striker','high_sr']].merge(
        low_p[['striker','low_sr']], on='striker')
    merged['drop'] = (merged['low_sr'] - merged['high_sr']).round(1)
    merged = merged.merge(
        batting_stats[['striker','total_runs']], on='striker')
    merged = merged[merged['total_runs'] >= 1000]
    clutch = merged.nsmallest(15, 'drop')

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name='Low Pressure SR', x=clutch['striker'],
        y=clutch['low_sr'], marker_color=COLORS['green']))
    fig2.add_trace(go.Bar(
        name='High Pressure SR', x=clutch['striker'],
        y=clutch['high_sr'], marker_color=COLORS['accent']))
    fig2.update_layout(
        paper_bgcolor=COLORS['card'],
        plot_bgcolor=COLORS['card'],
        font_color=COLORS['text'],
        title='Most Clutch Batters (Min 1000 IPL runs)',
        barmode='group', height=380)
    fig2.update_xaxes(gridcolor=COLORS['border'], tickangle=45)
    fig2.update_yaxes(gridcolor=COLORS['border'])
    return fig1, fig2

# ── Run ───────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=8050)