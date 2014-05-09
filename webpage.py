#!/usr/bin/env python 

import os
import re
from argparse import ArgumentParser

DEFAULT_IONS_PER_PAGE = 10
DEFAULT_MZ_DELTA = 6.0201

def parse_args():
    parser = ArgumentParser(
        description = 'Web pages for twin ion results')
    parser.add_argument(
        '--hits', metavar='FILE', type=str, required=True,
        help='FILE containing list of twin ion hits for case')
    parser.add_argument(
        '--eic_graphs', metavar='FILE', type=str, default='eic_graphs',
        help='path to directory containing eic graphs')
    parser.add_argument(
        '--threed_graphs', metavar='FILE', type=str, default='3d',
        help='path to directory containing 3D plots')
    parser.add_argument(
        '--ions_per_page', metavar='INT', type=int, default=DEFAULT_IONS_PER_PAGE,
        help='number of twin ion hits per page')
    parser.add_argument(
        '--mz_delta', metavar='FLOAT', type=float, default=DEFAULT_MZ_DELTA,
        help='m/z difference between heavy and light ion')
    return parser.parse_args()


doc_template = '''
<!DOCTYPE html>
<html>
   <head>
   <title>Twin Ion Results</title>
        <link rel="stylesheet" href="http://yui.yahooapis.com/pure/0.4.2/pure-min.css">
        <link rel="stylesheet" href="side-menu.css">
        <link rel="stylesheet" href="custom.css">
   </head>
   <body>
      <div id="layout">
         <div id="main">
            <div class="header">
               <h1>Twin Ion Results</h1>
               <h2>{hit_low} - {hit_high}</h2>
            </div>
         <div id="menu">
            <div class="pure-menu pure-menu-open">
               <ul>
                  {paginator}
               </ul>
            </div>
         </div>
         <div class="content">
            {body}
         </div>
      </div>
   </body>
</html>
'''

entry_template = '''
<h2>Hit {hit}</h2>
<p>
<table class="pure-table">
   <thead>
   <tr><th>m/z low</th><th>m/z high</th><th>time</th><th>intensity</th><th>score</th></tr>
   </thead>
   <tr><td>{mass_low:.3f}</td><td>{mass_high:.3f}</td><td>{time:.3f}</td><td>{intensity:}</td><td>{score:.3f}</td></tr>
</table>
</p>
<p>
<a href="{plot_3d}">3D plot</a>
</p>
<p>
<img src="{eic_graph}">
</p>
'''

def paginator(num_pages):
    result = []
    for page_num in range(1, num_pages + 1):
        result.append('<li><a href="ions_{0}.html">{0}</a></li>'.format(page_num))
    return '\n'.join(result)

def main():
    args = parse_args()
    process_hits(args)

def process_hits(args):
    with open(args.hits) as hits_file:
        hit_lines = list(hits_file)
        total_hits = len(hit_lines)
        total_pages = total_hits // args.ions_per_page 
        page_links = paginator(total_pages)
        for page_count, hit_group in enumerate(group(enumerate(hit_lines, 1), args.ions_per_page), 1):
            page_hit_low = None
            entries = []
            for count, line in hit_group:
                if page_hit_low is None:
                    page_hit_low = count
                fields = line.split(',')
                time, mass, intensity, score = fields[:4]
                time = float(time.strip())
                mass_low = float(mass.strip())
                intensity = float(intensity.strip())
                score = float(score.strip())
                mass_high = mass_low + args.mz_delta 
                path_eic_graph = os.path.join(args.eic_graphs, 'hit_' + str(count) + '.svg')
                path_3d = os.path.join(args.threed_graphs, 'hit_' + str(count) + '.html')
                new_entry = entry_template.format(hit=count, eic_graph=path_eic_graph, 
                                mass_low=mass_low, mass_high=mass_high, time=time, intensity=intensity,
                                score=score, plot_3d=path_3d)
                entries.append(new_entry)
            body = '\n'.join(entries)
            with open('ions_{}.html'.format(page_count), 'w') as html_page:
                html_page.write(doc_template.format(body=body, paginator=page_links, hit_low=page_hit_low, hit_high=count))

def group(iterator, size):
    chunk = []
    for item in iterator:
        if len(chunk) == size - 1:
            chunk.append(item)
            yield chunk
            chunk = []
        else:
            chunk.append(item)
    if chunk:
        yield chunk

if __name__ == '__main__':
    main()
