"""Render concise factual chart from the saved measurements."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent


def main():
    summary=json.loads((ROOT/'results/summary.json').read_text())
    assert summary['status']=='completed'
    groups={(g['model'],g['condition']):g for g in summary['groups']}
    models=['qwen2.5:7b','qwen3:8b'];conditions=['full64','lexical4']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.titlesize':17,'axes.labelsize':13,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(12,5.1),layout='constrained')
    colors=['#2166ac','#d6604d'];labels=['All 64 tools','Lexical top 4']
    for column,(field,title,ylabel) in enumerate([('exact','Usable tool calls','Calls'),('prompt_eval_count','Mean prompt tokens','Tokens')]):
        ax=axes[column]
        for ci,condition in enumerate(conditions):
            values=[]
            for model in models:
                g=groups[model,condition]
                if field=='exact':value=g[field]
                else:
                    assert g[field]['known']==16
                    value=g[field]['mean']
                values.append(value)
            bars=ax.bar([i+(ci-.5)*.34 for i in range(2)],values,width=.32,color=colors[ci],label=labels[ci])
            for bar,value in zip(bars,values):
                label=f'{value}/16' if field=='exact' else f'{value:,.1f}'
                ax.annotate(label,(bar.get_x()+bar.get_width()/2,bar.get_height()),xytext=(0,6),textcoords='offset points',ha='center',fontsize=12,fontweight='bold')
        ax.set_title(title,pad=15);ax.set_ylabel(ylabel)
        ax.set_xticks([0,1],['Qwen2.5 7B','Qwen3 8B']);ax.set_axisbelow(True)
        ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
        if field=='exact':ax.set_ylim(0,18.7);ax.set_yticks([0,4,8,12,16])
        else:ax.set_ylim(0,max(groups[m,c][field]['max'] for m in models for c in conditions)*1.2)
    axes[0].legend(loc='upper left',frameon=False,fontsize=11)
    fig.savefig(ROOT/'results/tool-catalog.png',dpi=200)
    fig.savefig(ROOT/'results/tool-catalog.svg')
    plt.close(fig)


if __name__=='__main__':main()
