"""
dashboard/app.py — StrepA AMR Genomic Surveillance Dashboard
Reads: ../results/summary.tsv
 
Usage:
    pip install dash plotly pandas
    python app.py
    open http://127.0.0.1:8050
"""
import os
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
 
# ── Load data ─────────────────────────────────────────────────────────────────
TSV = os.path.join(os.path.dirname(__file__), '..', 'results', 'summary.tsv')
 
df = pd.read_csv(TSV, sep='\t', dtype={'ST': str, 'emm_type': str})
df['has_amr'] = df['amr_genes'] != 'none'
 
# AMR genes — explode to one gene per row
amr_df = df[df['has_amr']].copy()
amr_df['gene_list'] = amr_df['amr_genes'].str.split(';')
amr_long = amr_df.explode('gene_list').rename(columns={'gene_list': 'gene'})
 
gene_counts = (amr_long.groupby('gene')['sample_id']
               .nunique().reset_index()
               .rename(columns={'sample_id': 'n'})
               .sort_values('n', ascending=False))
 
# Resistance classes
CLASS_MAP = {
    'tet(M)': 'Tetracycline',  'tet(O)': 'Tetracycline',
    'tet(T)': 'Tetracycline',  'tet(L)': 'Tetracycline',
    'erm(B)': 'Macrolide',     'erm(A)': 'Macrolide',
    'erm(T)': 'Macrolide',     'erm(C)': 'Macrolide',
    'mef(A)': 'Macrolide',     'msr(D)': 'Macrolide',
    'msr(I)': 'Macrolide',     'mef(J)': 'Macrolide',
    'dfrG':   'Trimethoprim',  'dfrF':  'Trimethoprim',
    'thfT':   'Trimethoprim',
    "aph(3')-IIIa": 'Aminoglycoside',
    'ant(6)-Ia':    'Aminoglycoside',
    'ant(9)-Ib':    'Aminoglycoside',
    'sat4':   'Streptothricin',
    'catA':   'Chloramphenicol',
}
amr_long['class'] = amr_long['gene'].map(CLASS_MAP).fillna('Other')
class_counts = (amr_long.groupby('class')['sample_id']
                .nunique().reset_index()
                .rename(columns={'sample_id': 'n'})
                .sort_values('n', ascending=False))
 
# MLST
st_counts = (df.groupby('ST').size().reset_index(name='n')
             .sort_values('n', ascending=False))
st_top20 = st_counts.head(20).copy()
st_top20['label'] = 'ST' + st_top20['ST']
 
# emm types
emm_counts = (df.groupby('emm_type').size().reset_index(name='n')
              .sort_values('n', ascending=False))
emm_counts['label'] = 'emm' + emm_counts['emm_type']
 
# AMR by emm type
amr_by_emm = (df.groupby('emm_type')
              .agg(total=('sample_id', 'count'), amr_pos=('has_amr', 'sum'))
              .reset_index())
amr_by_emm['clean']   = amr_by_emm['total'] - amr_by_emm['amr_pos']
amr_by_emm['pct']     = (amr_by_emm['amr_pos'] / amr_by_emm['total'] * 100).round(1)
amr_by_emm['label']   = 'emm' + amr_by_emm['emm_type']
amr_by_emm = amr_by_emm.sort_values('total', ascending=False)
 
# KPI numbers
N          = len(df)
N_AMR      = int(df['has_amr'].sum())
AMR_PCT    = f"{N_AMR/N*100:.1f}%"
N_STS      = df['ST'].nunique()
TOP_ST     = f"ST{st_counts.iloc[0]['ST']}  ({st_counts.iloc[0]['n']})"
N_EMM      = df['emm_type'].nunique()
TOP_EMM    = f"emm{emm_counts.iloc[0]['emm_type']}  ({emm_counts.iloc[0]['n']})"
 
# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = '#1F4E79'
BLUE   = '#2E75B6'
LBLUE  = '#D6E4F0'
RED    = '#C0392B'
LRED   = '#FADBD8'
BG     = '#F0F4F8'
CARD   = '#FFFFFF'
GREY   = '#666666'
 
CLASS_COLORS = {
    'Tetracycline':    '#2471A3',
    'Macrolide':       '#1A5276',
    'Trimethoprim':    '#5DADE2',
    'Aminoglycoside':  '#85C1E9',
    'Streptothricin':  '#AED6F1',
    'Chloramphenicol': '#D6EAF8',
    'Other':           '#BDC3C7',
}
 
# ── Layout helpers ────────────────────────────────────────────────────────────
def card(children, flex=1, min_width='140px', border_color=BLUE):
    return html.Div(children, style={
        'background': CARD, 'borderRadius': '8px',
        'padding': '18px 22px', 'flex': str(flex),
        'boxShadow': '0 1px 5px rgba(0,0,0,0.08)',
        'borderTop': f'4px solid {border_color}',
        'minWidth': min_width,
    })
 
def kpi(value, label, color=BLUE):
    return card([
        html.Div(str(value), style={
            'fontSize': '2rem', 'fontWeight': '700',
            'color': color, 'lineHeight': '1.1',
        }),
        html.Div(label, style={
            'fontSize': '0.82rem', 'color': GREY,
            'marginTop': '5px', 'fontWeight': '500',
        }),
    ], border_color=color)
 
def plot_card(fig, flex=1):
    return html.Div(dcc.Graph(figure=fig, config={'displayModeBar': False}),
                    style={'background': CARD, 'borderRadius': '8px',
                           'padding': '8px', 'flex': str(flex),
                           'boxShadow': '0 1px 5px rgba(0,0,0,0.07)'})
 
def row(*children, gap='20px'):
    return html.Div(list(children),
                    style={'display': 'flex', 'gap': gap,
                           'flexWrap': 'wrap', 'alignItems': 'stretch'})
 
BASE_LAYOUT = dict(
    plot_bgcolor=CARD, paper_bgcolor=CARD,
    font=dict(family='Arial', size=12),
    hoverlabel=dict(bgcolor='white', font_size=12),
)
 
# ── Figures ───────────────────────────────────────────────────────────────────
def fig_genes():
    top = gene_counts.head(20).sort_values('n')
    colors = [RED if i == len(top) - 1 else BLUE
              for i in range(len(top))]
    fig = go.Figure(go.Bar(
        x=top['n'], y=top['gene'],
        orientation='h',
        marker_color=colors,
        text=top['n'], textposition='outside',
        hovertemplate='<b>%{y}</b>: %{x} strains<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(text='AMR Gene Frequency', font=dict(color=NAVY, size=14)),
        height=520,
        xaxis=dict(title='Strains (n)', gridcolor='#EEE'),
        yaxis=dict(tickfont=dict(size=11)),
    )
    return fig
 
def fig_classes():
    colors = [CLASS_COLORS.get(c, '#BDC3C7') for c in class_counts['class']]
    fig = go.Figure(go.Bar(
        x=class_counts['class'], y=class_counts['n'],
        marker_color=colors,
        text=class_counts['n'], textposition='outside',
        hovertemplate='<b>%{x}</b>: %{y} strains<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(text='Strains by Resistance Class', font=dict(color=NAVY, size=14)),
        height=360,
        yaxis=dict(title='Strains (n)', gridcolor='#EEE'),
        xaxis=dict(tickangle=-20),
    )
    return fig
 
def fig_mlst():
    colors = [RED if i == 0 else BLUE for i in range(len(st_top20))]
    colors_rev = list(reversed(colors))
    fig = go.Figure(go.Bar(
        x=list(reversed(st_top20['n'].tolist())),
        y=list(reversed(st_top20['label'].tolist())),
        orientation='h',
        marker_color=colors_rev,
        text=list(reversed(st_top20['n'].tolist())),
        textposition='outside',
        hovertemplate='<b>%{y}</b>: %{x} genomes<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(
            text=f'MLST — Top 20 Sequence Types  ({N_STS} unique STs total)',
            font=dict(color=NAVY, size=14)
        ),
        height=560,
        xaxis=dict(title='Genomes (n)', gridcolor='#EEE'),
        yaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=10, r=60, t=50, b=10),
    )
    return fig
 
def fig_emm():
    pcts = (emm_counts['n'] / N * 100).round(1)
    colors = [RED if i == 0 else BLUE for i in range(len(emm_counts))]
    fig = go.Figure(go.Bar(
        x=emm_counts['label'], y=emm_counts['n'],
        marker_color=colors,
        text=[f"{n}<br>({p}%)" for n, p in zip(emm_counts['n'], pcts)],
        textposition='outside',
        hovertemplate='<b>%{x}</b>: %{y} genomes<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(
            text=f'emm Type Distribution  ({N_EMM} types identified)',
            font=dict(color=NAVY, size=14)
        ),
        height=420,
        yaxis=dict(title='Genomes (n)', gridcolor='#EEE'),
        xaxis=dict(tickfont=dict(size=12)),
    )
    return fig
 
def emm_table():
    header = html.Tr([
        html.Th(h, style={'padding': '8px 12px', 'textAlign': 'left',
                          'color': NAVY, 'borderBottom': f'2px solid {BLUE}'})
        for h in ['emm type', 'Genomes (n)', '% of collection']
    ], style={'background': LBLUE})
    rows = []
    for i, rec in enumerate(emm_counts.to_dict('records')):
        pct = round(rec['n'] / N * 100, 1)
        rows.append(html.Tr([
            html.Td(rec['label'],  style={'padding': '7px 12px', 'fontWeight': '600'}),
            html.Td(str(rec['n']), style={'padding': '7px 12px'}),
            html.Td(f"{pct}%",     style={'padding': '7px 12px'}),
        ], style={'background': '#EBF3FA' if i % 2 == 1 else CARD}))
    return html.Table([header] + rows, style={
        'width': '100%', 'borderCollapse': 'collapse',
        'fontFamily': 'Arial', 'fontSize': '0.9rem',
    })
 
def fig_amr_emm():
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='No AMR genes',
        x=amr_by_emm['label'], y=amr_by_emm['clean'],
        marker_color=LBLUE,
        hovertemplate='<b>%{x}</b> — clean: %{y}<extra></extra>',
    ))
    fig.add_trace(go.Bar(
        name='AMR positive',
        x=amr_by_emm['label'], y=amr_by_emm['amr_pos'],
        marker_color=RED,
        text=[f"{p}%" for p in amr_by_emm['pct']],
        textposition='outside',
        hovertemplate='<b>%{x}</b> — AMR+: %{y} (%{text})<extra></extra>',
    ))
    fig.update_layout(**BASE_LAYOUT,
        title=dict(
            text='AMR Carriage by emm Type  (% label = AMR+ within emm type)',
            font=dict(color=NAVY, size=14)
        ),
        barmode='stack',
        height=440,
        yaxis=dict(title='Genomes (n)', gridcolor='#EEE'),
        xaxis=dict(title='emm type', tickfont=dict(size=12)),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1),
    )
    fig.update_layout(margin=dict(l=10, r=20, t=80, b=10))
    return fig
 
# ── App layout ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title='StrepA AMR Dashboard')
app.layout = html.Div([
 
    # Header
    html.Div([
        html.Div([
            html.Span('Streptococcus pyogenes', style={
                'fontStyle': 'italic', 'fontWeight': '700',
                'fontSize': '1.45rem', 'color': NAVY,
            }),
            html.Span('  Genomic Surveillance', style={
                'fontWeight': '700', 'fontSize': '1.45rem', 'color': NAVY,
            }),
            html.Div(
                'AMR Profiling · MLST · emm Typing  |  375 Genomes  |  StrepA-AMR-pipeline',
                style={'color': GREY, 'fontSize': '0.88rem', 'marginTop': '4px'}
            ),
        ]),
        html.Div('bkhimek / StrepA-AMR-pipeline', style={
            'color': BLUE, 'fontSize': '0.82rem',
            'fontFamily': 'monospace', 'alignSelf': 'center',
        })
    ], style={
        'display': 'flex', 'justifyContent': 'space-between',
        'alignItems': 'flex-start',
        'background': CARD, 'padding': '18px 32px',
        'borderBottom': f'3px solid {BLUE}',
        'boxShadow': '0 2px 6px rgba(0,0,0,0.06)',
    }),
 
    # KPI row
    html.Div(row(
        kpi(N,                  'Total genomes'),
        kpi(f'{N_AMR} ({AMR_PCT})', 'Carry AMR genes',       RED),
        kpi(N_STS,              'Unique STs'),
        kpi(TOP_ST,             'Most common ST',            NAVY),
        kpi(N_EMM,              'emm types identified'),
        kpi(TOP_EMM,            'Most common emm type',      NAVY),
    ), style={'padding': '20px 32px', 'background': BG}),
 
    # Tabs
    html.Div([
        dcc.Tabs(id='tabs', value='amr', children=[
            dcc.Tab(label='🧬  AMR Genes',        value='amr',     className='tab'),
            dcc.Tab(label='🔬  MLST',             value='mlst',    className='tab'),
            dcc.Tab(label='🏷  emm Typing',        value='emm',     className='tab'),
            dcc.Tab(label='📊  AMR × emm Type',   value='amr_emm', className='tab'),
        ], style={'fontFamily': 'Arial'}),
        html.Div(id='content', style={'paddingTop': '20px'}),
    ], style={'padding': '4px 32px 32px', 'background': BG}),
 
    # Footer
    html.Div([
        "Part of Krzysztof Gizynski's bioinformatics consulting portfolio  |  ",
        html.A('github.com/bkhimek',
               href='https://github.com/bkhimek',
               style={'color': BLUE, 'textDecoration': 'none'}),
    ], style={
        'textAlign': 'center', 'padding': '18px',
        'fontSize': '0.8rem', 'color': '#999',
        'borderTop': '1px solid #DDD', 'background': CARD,
    }),
 
], style={'fontFamily': 'Arial, sans-serif', 'background': BG, 'minHeight': '100vh'})
 
 
@app.callback(Output('content', 'children'), Input('tabs', 'value'))
def render(tab):
 
    if tab == 'amr':
        return html.Div([
            row(plot_card(fig_genes(), flex=1.5),
                plot_card(fig_classes(), flex=1))
        ])
 
    if tab == 'mlst':
        return html.Div([
            row(plot_card(fig_mlst()))
        ])
 
    if tab == 'emm':
        return row(
            plot_card(fig_emm(), flex=1.6),
            html.Div(
                emm_table(),
                style={'flex': '1', 'background': CARD, 'borderRadius': '8px',
                       'padding': '16px 20px',
                       'boxShadow': '0 1px 5px rgba(0,0,0,0.07)'}
            )
        )
 
    if tab == 'amr_emm':
        return html.Div([
            row(plot_card(fig_amr_emm()))
        ])
 
 
if __name__ == '__main__':
    app.run(debug=True)
