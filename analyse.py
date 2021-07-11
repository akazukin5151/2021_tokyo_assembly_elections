import json

import pandas as pd
import geopandas as gpd
from shapely.ops import unary_union
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
#from matplotlib import rcParams


with open('processed_results.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame.from_records(data, columns=['district', 'votes', 'party'])

# Final fixes to the data set
df.votes = df.votes.str.replace(',', '').astype(int)
party_fixes = {
    '自民（公）': '自民',
    '立民（社）': '立民',
    '立民（ネ）': '立民',
    '立民（ネ・社）': '立民',
    '諸派（嵐）': '諸派',
    '共産（社）': '共産',
    '無所属（立・ネ・社）': '無所属',
    '無所属（共・立・ネ・社）': '無所属',
    'ネット（立）': 'ネット'  # Nothing duplicated with this, just reducing text
}
df.party.replace(party_fixes, inplace=True)


# To deal with Japanese text
#rcParams['font.family'] = 'Hiragino Sans GB'

# Plot bar charts
grouped = df.groupby(['district', 'party'])['votes'].sum().unstack(fill_value=0)
grouped['Total'] = grouped.sum(axis=1)
grouped = grouped.sort_values('Total')
#grouped.plot.barh(stacked=True)
#plt.show()

grouped_pct = grouped.apply(lambda r: r / r.Total * 100, axis=1)
del grouped_pct['Total']
grouped_pct.sort_values('自民', inplace=True)
#grouped_pct.plot.barh(stacked=True)
#plt.show()


# Plot a map
tokyo = gpd.read_file('Tokyo_boundaries.geojson')

# Merge some districts
def merger(tokyo: 'gdf', names: list[str], eng: str, jp: str) -> 'gdf':
    union = unary_union((tokyo[(tokyo.NL_NAME_2).isin(names)].geometry).to_list())
    row = [(
        'JPN',
        'Japan',
        'JPN.41_1',
        'Tokyo',
        '東京都',
        'JPN.41.1_1',
        eng,
        None,
        jp,
        'Special Ward',
        'Special Ward',
        None,
        None,
        union
    )]
    sub = gpd.GeoDataFrame.from_records(row, columns=tokyo.columns)
    return tokyo.append(sub)

def batch_merge(tokyo: 'gdf') -> 'gdf':
    # https://www.senkyo.metro.tokyo.lg.jp/election/kakushu-teisuu/togi-teisuu-list1/
    data = [
        ('西多摩', 'Nishi-Tama', [
            '福生市',
            '羽村市',
            'あきる野市',
            '瑞穂町',
            '日の出町',
            '檜原村',
            '奥多摩町'
        ]),
        ('南多摩', 'Minami-Tama', ['多摩市', '稲城市']),
        ('北多摩一', 'Kita-Tama-1', ['東村山市', '東大和市', '武蔵村山市']),
        ('北多摩二', 'Kita-Tama-2', ['国分寺市', '国立市']),
        ('北多摩三', 'Kita-Tama-3', ['調布市', '狛江市']),
        ('北多摩四', 'Kita-Tama-4', ['清瀬市', '東久留米市']),
    ]
    for jp, eng, names in data:
        tokyo = merger(tokyo, names, eng, jp)

    return tokyo

tokyo = batch_merge(tokyo)

merged = tokyo.merge(grouped_pct, left_on='NL_NAME_2', right_on='district')
max_v = 62.148199  # Ome; island isn't visible on map

fig = plt.figure()
grid = ImageGrid(
    fig,
    111,
    nrows_ncols=(3,4),
    share_all=True,
    cbar_mode='single',
    cbar_location='bottom',
)

def args(party):
    return dict(
        column=party,
        cmap='Greens',
        ax=ax,
        edgecolor='gray',
        lw=0.5,
        vmax=max_v,
    )

legend = True
for ax, party in zip(grid, df['party'].unique()):
    if legend:
        cax = grid.cbar_axes[0]
        extra = dict(
            legend=True,
            legend_kwds={'orientation': 'horizontal', 'label': 'Vote %'},
            cax=cax
        )
        new = args(party) | extra
        merged.plot(**new)
        cax.tick_params(labelsize=7)
        # Has to be repeated for some reason
        cax.set_xlabel('Vote %', fontsize=8)
        legend = False
    else:
        merged.plot(**args(party))
    ax.set_title(party, y=0.75, fontsize=7, fontfamily='Hiragino Sans GB')
    ax.set_xticks([])
    ax.set_yticks([])

plt.tight_layout()
#plt.show()
plt.savefig('out.png', dpi=300)

