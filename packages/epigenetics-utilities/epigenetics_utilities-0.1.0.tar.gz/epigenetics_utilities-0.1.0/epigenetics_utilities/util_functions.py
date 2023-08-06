import os
import sys
import re
import inspect
import seaborn as sns
import pandas as pd
import numpy as np
import itertools
from statannot import add_stat_annotation
from sklearn.model_selection import GridSearchCV

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial','Roboto']
rcParams['text.usetex'] = False
rcParams['svg.fonttype'] = 'none'
rcParams['mathtext.default'] = 'regular'

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

import mygene

SMALL_SIZE = 7
MEDIUM_SIZE = 9
BIGGER_SIZE = 12

plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=MEDIUM_SIZE)  # fontsize of the figure title

def string_to_dict(string, item_delimiter=',', pair_delimiter=None):
	if pair_delimiter is not None:
		string_dict = {item.split(pair_delimiter)[0]:item.split(pair_delimiter)[1] for item in string.split(item_delimiter) if len(item.split(pair_delimiter)) > 1}
	else:
		string_dict = {item.split()[0]:item.split()[1] for item in string.split(item_delimiter) if len(item.split()) > 1}
		
	return string_dict

def query_gtf_coordinates(path_gtf, sequence_type, identifier, gene_name_filter_list = None):
	
	#'/home/data/Shared/genome_reference_files/hg19/hg19.refGene.gtf'
	# sequence_type='transcript', identifier='gene_name'
	
	gtf_df = pd.read_csv(path_gtf, sep='\t', names=['chromosome', 'gene_id_source', 'sequence_type', 'start', 'stop', 'null1', 'strand', 'null2', 'id_data'])
	
	gtf_df_transcripts = gtf_df.loc[gtf_df['sequence_type'] == sequence_type]
	gtf_df_transcripts_records = gtf_df_transcripts.to_records()
	
	gene_coordinate_dict = {string_to_dict(record['id_data'], item_delimiter=';', pair_delimiter=None)[identifier].replace('"', ''): [str(record['chromosome']), int(record['start']), int(record['stop']), str(record['strand'])] for record in gtf_df_transcripts_records if identifier in string_to_dict(record['id_data'], item_delimiter=';', pair_delimiter=None)}
	
	if gene_name_filter_list is not None:
	
		filtered_gene_coordinate_dict = {gene_name: gene_coordinate_dict[gene_name] for gene_name in gene_name_filter_list if gene_name in gene_coordinate_dict}
		print(len(gene_name_filter_list) - len(filtered_gene_coordinate_dict), 'genes not found in gtf')
		return filtered_gene_coordinate_dict
		
	else:
		
		return gene_coordinate_dict


def query_mygene_coordinates(gene_id_list, *ignore, scopes=None, genome=None):
	
	"""
	
	Queries the mygene.info database with a list of gene names/ids and returns a dictionary with their coordinates.

	:param gene_id_list:	A list of query terms, should be gene ids/names in string format
	
	:param scopes: 		A list of of types of gene ids/names that should be matched to, in descending order of priority.
				Should contain any of the following: ['ensembl', 'entrezgene', 'refseq', 'symbol', 'alias', 'name', 'other_names']
				Pass multiple in the event that your list of gene ids/names aren't all the same type.
				For example, if list contains some outdated gene symbols, add 'alias' as an additional scope.
				In the event of a duplicate, the highest priority scope will match the query term.
							
	:param genome:		'hg19' or 'hg38'
	
	
	Example:
	
	>>> query_coordinates(['YATS2'], scopes=['symbol','alias'], genome='hg19')
	
	"""
	
	# some incorrect arugments
	if ignore:  # If ignore is not empty
		raise TypeError("Incorrect arguments provided. Example usage: query_coordinates([['YEATS2']], scopes=['symbol','alias'], genome=hg19)")
	
	# check scopes
	if type(scopes) != list:
		raise TypeError("Invalid 'scopes' argument. Scopes should be a list of potential name/id types in string form that you would like to match to.\nAny of the following: ['ensembl', 'entrezgene', 'refseq', 'symbol', 'alias', 'name', 'other_names']. Pass in order of descending importance in case of duplicate return values.")
		
	valid_scopes = ['ensembl', 'entrezgene', 'refseq', 'symbol', 'alias', 'name', 'other_names']
	
	if any(scope not in valid_scopes for scope in scopes):
		raise NameError("Invalid entry in 'scopes' argument.\nShould contain any of the following: ['ensembl', 'entrezgene', 'refseq', 'symbol', 'alias', 'name', 'other_names']. Pass in order of descending importance in case of duplicate return values.")
	
	# check genome
	if genome != 'hg19' and genome != 'hg38':
		raise NameError("Invalid 'genome' argument. Should be either 'hg19' or 'hg38' as a string")

	mg = mygene.MyGeneInfo()
	
	if genome == 'hg19':
		position_field = 'genomic_pos_hg19'
	elif genome == 'hg38':
		position_field = 'genomic_pos'
		
	mg_response = mg.querymany(gene_id_list, scopes=scopes, species='human', fields=position_field)
	
	mg_response_dict = {}
	for gene in mg_response:
		if position_field in gene:
			if gene['query'] in mg_response_dict:
				# this is the duplicate entry case
				# remap this if the current gene symbol matches the current gene query
				
				if gene['query'] not in mg_response_dict:
					mg_response_dict[gene['query']] = gene[position_field]
				else:
					# check scope to see if existing entry should be rewritten
					for scope in reversed(scopes):
						if scope in gene:
							if gene[scope] == gene['query']:
								mg_response_dict[gene['query']] = gene[position_field]
			else:
				mg_response_dict[gene['query']] = gene[position_field]
		elif gene['query'] not in mg_response_dict:
			mg_response_dict[gene['query']] = 'not found'
	
	return mg_response_dict

def savefile_with_readme(args, stack, path_file, data_file_string):
	
	with open(path_file, 'w') as file:
		file.write(data_file_string)
	
	dirname = os.path.dirname(path_file)
	path_readme = os.path.join(dirname, 'README.txt')
	
	path_script = stack[0][1]
	
	text_stack = ['line: ' + str(trace[2]) + ', ' + str(trace[4][0]) for i, trace in enumerate(stack) if i > 0]
	text_stack.reverse()
	
	text_readme = '\n'.join(['Datafiles generated with: ' + path_script, 'Input arguments: ' + str(args), 'Stack:\n']) + ''.join(text_stack)
	
	with open(path_readme, 'w') as file:
		file.write(text_readme)

def savefig_with_readme(args, stack, path_fig):
	
	plt.savefig(path_fig)
	
	dirname = os.path.dirname(path_fig)
	path_readme = os.path.join(dirname, 'README.txt')
	
	path_script = stack[0][1]
	
	text_stack = ['line: ' + str(trace[2]) + ', ' + str(trace[4][0]) for i, trace in enumerate(stack) if i > 0]
	text_stack.reverse()
	
	text_readme = '\n'.join(['Figures generated with: ' + path_script, 'Input arguments: ' + str(args), 'Stack:\n']) + ''.join(text_stack)
	
	with open(path_readme, 'w') as file:
		file.write(text_readme)

def atoi(text):
	return int(text) if text.isdigit() else text

def natural_keys(text):
	'''
	alist.sort(key=natural_keys) sorts in human order
	http://nedbatchelder.com/blog/200712/human_sorting.html
	(See Toothy's implementation in the comments)
	'''
	return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def bam_file(filename):
	ext = [".bam", ".sam"]
	return filename.endswith(tuple(ext))

def bed_file(filename):
	ext = [".bed"]
	return filename.endswith(tuple(ext))

def bigwig_file(filename):
	ext = [".bigWig", ".bigwig", ".bw"]
	return filename.endswith(tuple(ext))

def newline(p1, p2):
	ax = plt.gca()
	xmin, xmax = ax.get_xbound()

	if(p2[0] == p1[0]):
		xmin = xmax = p1[0]
		ymin, ymax = ax.get_ybound()
	else:
		ymax = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmax-p1[0])
		ymin = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmin-p1[0])

	l = mlines.Line2D([xmin,xmax], [ymin,ymax])
	ax.add_line(l)
	return l

def newtext(s, corner):
	ax = plt.gca()
	xmin, xmax = ax.get_xbound()
	ymin, ymax = ax.get_ybound()

	if corner == 'top-right':
		x = xmax * 0.98
		y = ymax * 0.98
		plt.text(x,y,s, horizontalalignment='right', verticalalignment = 'top')
	elif corner == 'top-left':
		x = xmin + (xmax - xmin)*0.02
		y = ymax * 0.98
		plt.text(x,y,s, horizontalalignment='left', verticalalignment = 'top')
	elif corner == 'bottom-left':
		x = xmin + (xmax - xmin)*0.02
		y = ymin + (ymax - ymin)*0.02
		plt.text(x,y,s, horizontalalignment='left', verticalalignment = 'bottom')
	elif corner == 'bottom-right':
		x = xmax * 0.98
		y = ymin + (ymax - ymin)*0.02
		plt.text(x,y,s, horizontalalignment='right', verticalalignment = 'bottom')

def add_metric_to_box_plot(df, x, y, order, ax, metric, **kwargs):
	
	unique_xs = order
	metrics = {}
	medians = {}
	pos = {}
	
	for i, unique_x in enumerate(unique_xs):
		df_x = df.loc[df[x] == unique_x]
		
		if metric == 'mean':
			metric_y = np.mean(df_x[y].tolist())
		elif metric == 'median':
			metric_y = np.median(df_x[y].tolist())
			
		median_y = np.median(df_x[y].tolist())
		
		metrics[unique_x] = metric + "=" + str(round(metric_y,3))
		medians[unique_x] = median_y
		pos[unique_x] = i
		
	# horizontalalignment='center', fontsize='x-small', color='w'
	 
	# Add it to the plot
	for tick, label in zip(pos, ax.get_xticklabels()):
		ax.text(pos[tick], medians[tick] + 0.03, metrics[tick], **kwargs)
		
def add_n_to_box_plot(df, x, y, order, ax, **kwargs):
	
	unique_xs = order
	medians = {}
	nobs = {}
	pos = {}
	
	for i, unique_x in enumerate(unique_xs):
		df_x = df.loc[df[x] == unique_x]
		nob = str(len(df_x.index))
		median_y = np.median(df_x[y].tolist())
		
		medians[unique_x] = median_y
		nobs[unique_x] = "n=" + nob
		pos[unique_x] = i
		
	# horizontalalignment='center', fontsize='x-small', color='w'
	 
	# Add it to the plot
	for tick, label in zip(pos, ax.get_xticklabels()):
		ax.text(pos[tick], medians[tick] + 0.03, nobs[tick], **kwargs)
		
def set_size(w,h, ax=None):
	""" w, h: width, height in inches """
	if not ax: ax=plt.gca()
	l = ax.figure.subplotpars.left
	r = ax.figure.subplotpars.right
	t = ax.figure.subplotpars.top
	b = ax.figure.subplotpars.bottom
	figw = float(w)/(r-l)
	figh = float(h)/(t-b)
	ax.figure.set_size_inches(figw, figh)

def plot_kde(df, x_name, filename, path_plot_dir, xlim=None, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	sns.kdeplot(data=df, x=x_name, ax=ax, **kwargs)
		
	if xlim is not None:
		ax.set_xlim(xlim)
	
	# plot for viewing
	path_png = os.path.join(path_plot_dir, filename + '.png')
	plt.title(title)
	plt.show()
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()	

def plot_2d_kde(x, y, filename, path_plot_dir, ylim=None, xlim=None, xlabel=None, ylabel=None, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	ax = sns.kdeplot(x=x, y=y, **kwargs)
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
	
	if ylim is not None:
		ax.set_ylim(ylim)
		
	if xlim is not None:
		ax.set_xlim(xlim)	
	
	if title is not None:
		plt.title(title)
		
	plt.show()
	path_png = os.path.join(path_plot_dir, filename + '.png')
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()


def plot_scatter_list(x, y, filename, path_plot_dir, ylim=None, xlim=None, xlabel=None, ylabel=None, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	ax = sns.scatterplot(x=x, y=y, **kwargs)
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
	
	if ylim is not None:
		ax.set_ylim(ylim)
		
	if xlim is not None:
		ax.set_xlim(xlim)	
	
	if title is not None:
		plt.title(title)
		
	plt.show()
	path_png = os.path.join(path_plot_dir, filename + '.png')
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()
	
def plot_hist(df, x_name, filename, path_plot_dir, ylim=None, xlim=None, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	sns.histplot(data=df, x=x_name, ax=ax, **kwargs)
	
	if ylim is not None:
		ax.set_ylim(ylim)
		
	if xlim is not None:
		ax.set_xlim(xlim)
	
	# plot for viewing
	path_png = os.path.join(path_plot_dir, filename + '.png')
	plt.title(title)
	plt.show()
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()	

def plot_hist_list(data_list, filename, path_plot_dir, ylim=None, xlim=None, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	sns.histplot(data_list, ax=ax, **kwargs)
	
	if ylim is not None:
		ax.set_ylim(ylim)
		
	if xlim is not None:
		ax.set_xlim(xlim)
	
	# plot for viewing
	path_png = os.path.join(path_plot_dir, filename + '.png')
	plt.title(title)
	plt.show()
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()
	
def plot_violin(df, x, y, order, filename, path_plot_dir, fig_width=None, fig_height=None, palette_name=None, metric=None, stat_test=None, rotate_x=False, xlabel=None, ylabel=None, ylim=None, hue=None, hue_order=None, pad_top=False, pad_bottom=False, pad_left=False, pad_right=False, title=None, **kwargs):
	
	if pad_top and pad_bottom:
		fig, ax = plt.subplots(figsize = (8, 10))
	elif (pad_top and not pad_bottom) or (pad_bottom and not pad_top):
		fig, ax = plt.subplots(figsize = (8, 8))
		
	if pad_top:
		fig.subplots_adjust(top=0.55)
	if pad_bottom:
		fig.subplots_adjust(bottom=0.45)
	if pad_left:
		fig.subplots_adjust(left=0.25)
	if pad_right:
		fig.subplots_adjust(right=0.85)
	
	#palette=sns.color_palette(palette_name, n_colors=len(order))
		
	# in a violin plot, 'x' serves as the hue
		
	if hue is not None and hue_order is not None:
		# for when there are inner categories
		sns.violinplot(data=df, x=x, y=y, ax=ax, order=order, hue=hue, hue_order=hue_order, **kwargs)
		if stat_test is not None:
			inner_categories = list(set(df[hue].tolist()))
			x_pairs = [((outer_category, inner_pair[0]), (outer_category, inner_pair[1])) for inner_pair in list(itertools.combinations(inner_categories, 2)) for outer_category in order]
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, hue=hue, test=stat_test, text_format='star', fontsize=SMALL_SIZE, loc='inside', verbose=1, linewidth=1, color='black')
	else:
		# only one set of categories
		sns.violinplot(data=df, x=x, y=y, ax=ax, order=order, **kwargs)
		if stat_test is not None:
			x_pairs = list(itertools.combinations(order, 2))
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, test=stat_test, text_format='star', fontsize=SMALL_SIZE, loc='inside', verbose=1, linewidth=1, color='black')
	
	if ylim is not None:
		ax.set_ylim(ylim)
	
	if metric is not None:
		add_metric_to_box_plot(df, x, y, order, ax, metric)
	
	path_png = os.path.join(path_plot_dir, filename + '.png')
	path_svg = path_png.replace('.png', '.svg')
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
	
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	
	if rotate_x:
		plt.xticks(rotation=45, ha='right')
	
	if title is not None:
		plt.title(title)
		
	plt.tight_layout()
		
	plt.show()
	
	if fig_width is not None and fig_height is not None:
		set_size(fig_width, fig_height, ax)
	
	savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()	
	
def plot_box(df, x, y, order, filename, path_plot_dir, fig_width=None, fig_height=None, palette_name=None, add_n=False, add_stat=False, rotate_x=False, xlabel=None, ylabel=None, ylim=None, hue=None, hue_order=None, pad_top=False, pad_bottom=False, pad_left=False, pad_right=False, title=None, **kwargs):
	
	fig, ax = plt.subplots()
	if pad_top:
		fig.subplots_adjust(top=0.55)
	if pad_bottom:
		fig.subplots_adjust(bottom=0.25)
	if pad_left:
		fig.subplots_adjust(left=0.25)
	if pad_right:
		fig.subplots_adjust(right=0.85)
	
	#palette=sns.color_palette(palette_name, n_colors=len(order))
		
	if hue is not None and hue_order is not None:
		sns.boxplot(data=df, x=x, y=y, ax=ax, order=order, hue=hue, hue_order=hue_order, **kwargs)
		if add_stat:
			inner_categories = list(set(df[hue].tolist()))
			x_pairs = [((outer_category, inner_pair[0]), (outer_category, inner_pair[1])) for inner_pair in list(itertools.combinations(inner_categories, 2)) for outer_category in order]
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, hue=hue, test='t-test_ind', text_format='star', fontsize=SMALL_SIZE, loc='outside', verbose=0, linewidth=1, color='black')
	else:
		sns.boxplot(data=df, x=x, y=y, ax=ax, order=order, **kwargs)
		if add_stat:
			x_pairs = list(itertools.combinations(order, 2))
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, test='t-test_ind', text_format='star', fontsize=SMALL_SIZE, loc='outside', verbose=0, linewidth=1, color='black')
		
	if ylim is not None:
		ax.set_ylim(ylim)
	
	if add_n:
		add_n_to_box_plot(df, x, y, order, ax)
	
	path_png = os.path.join(path_plot_dir, filename + '.png')
	path_svg = path_png.replace('.png', '.svg')
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
	
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	
	if rotate_x:
		plt.xticks(rotation=45, ha='right')
	
	
	if title is not None:
		plt.title(title)
		
	plt.show()
	
	if fig_width is not None and fig_height is not None:
		set_size(fig_width, fig_height, ax)
	
	savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()
	
def scale_num(new_max, new_min, old_max, old_min, val):
	return (new_max - new_min) * (val - old_min) / (old_max - old_min) + new_min
	
def plot_line(df, x_name, y_name, filename, path_plot_dir, hue=None, custom_ci_names=None, ylim=None, title=None, fig_width=None, fig_height=None, xticks=None, **kwargs):
	
	fig, ax = plt.subplots()
	
	if hue is not None:
		
		hue_order = list(set(df[hue].tolist()))
		hue_order.sort(key=natural_keys)
		palette=sns.color_palette("mako", n_colors=len(hue_order))
		
		# ci = 1.96 * np.std(y)/np.sqrt(len(x))
	
		if custom_ci_names is not None:
			lower_bound_name = custom_ci_names[0]
			upper_bound_name = custom_ci_names[1]
			for i, group in enumerate(hue_order):
				df_hue = df.loc[df[hue] == group]
				x = df_hue[x_name].tolist()
				lower_bound = df_hue[lower_bound_name].tolist()
				upper_bound = df_hue[upper_bound_name].tolist()
				plt.fill_between(x, lower_bound, upper_bound, color=palette[i], alpha=.33)
				
		sns.lineplot(data=df, x=x_name, y=y_name, hue=hue, hue_order=hue_order, ax=ax, palette=palette, **kwargs)
		plt.legend()
		
	else:
		sns.lineplot(data=df, x=x_name, y=y_name, ax=ax, **kwargs)
	
	if ylim is not None:
		ax.set_ylim(ylim)
	else:
		plt.autoscale()
		
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	
	if xticks is not None:
		ax.set_xticks(xticks)
		
	# plot for viewing
	path_png = os.path.join(path_plot_dir, filename + '.png')
	path_svg = path_png.replace('.png', '.svg')
	
	plt.title(title)
	plt.show()
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
	
	# plot for final figure
	if fig_width is not None and fig_height is not None:
		set_size(fig_width, fig_height, ax)
		
		path_png = os.path.join(path_plot_dir, filename + '.for_figure.png')
		path_svg = path_png.replace('.png', '.svg')
		
		savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
		savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
		
	plt.close()
	
def plot_bar(df, x, y, order, filename, path_plot_dir, fig_width=None, fig_height=None, add_n=False, add_stat=False, rotate_x=False, xlabel=None, ylabel=None, ylim=None, hue=None, hue_order=None, **kwargs):
	
	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.25, right=0.85, top=0.55, bottom=0.25)
	
	if hue is not None and hue_order is not None:
		sns.barplot(data=df, x=x, y=y, ax=ax, hue=hue, order=order, hue_order=hue_order, **kwargs)
		if add_stat:
			inner_categories = list(set(df[hue].tolist()))
			x_pairs = [((outer_category, inner_pair[0]), (outer_category, inner_pair[1])) for inner_pair in list(itertools.combinations(inner_categories, 2)) for outer_category in order]
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, hue=hue, test='t-test_ind', text_format='star', fontsize=SMALL_SIZE, loc='outside', verbose=1, linewidth=1, color='black')
	else:
		sns.barplot(data=df, x=x, y=y, ax=ax, order=order, hue=hue, **kwargs)
		if add_stat:
			x_pairs = list(itertools.combinations(order, 2))
			add_stat_annotation(ax, data=df, x=x, y=y, order=order, box_pairs=x_pairs, test='t-test_ind', text_format='star', fontsize=SMALL_SIZE, loc='outside', verbose=1, linewidth=1, color='black')
	
	path_png = os.path.join(path_plot_dir, filename + '.png')
	path_svg = path_png.replace('.png', '.svg')
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
		
	if ylim is not None:
		ax.set_ylim(ylim)
		
	if add_n:
		add_n_to_bar_plot(df, x, y, order, ax)
	
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	
	if rotate_x:
		plt.xticks(rotation=45, ha='right')
	
	plt.title(filename)
	plt.show()
	
	if fig_width is not None and fig_height is not None:
		set_size(fig_width, fig_height, ax)
	
	savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()
	
def add_n_to_bar_plot(df, x, y, order, ax):
	
	unique_xs = order
	means = {}
	nobs = {}
	pos = {}
	
	for i, unique_x in enumerate(unique_xs):
		df_x = df.loc[df[x] == unique_x]
		nob = str(len(df_x.index))
		mean_y = np.mean(df_x[y].tolist())
		
		means[unique_x] = mean_y
		nobs[unique_x] = "n=" + nob
		pos[unique_x] = i
	 
	# Add it to the plot
	for tick, label in zip(pos, ax.get_xticklabels()):
		ax.text(pos[tick], means[tick] + 0.1, nobs[tick], horizontalalignment='left', color='black', fontsize=SMALL_SIZE, rotation=45)

def add_stdev(df, x, y, order, ax, colors=None):
	
	lines = {}
	means = {}
	pos = {}
	colors_dict = {}
	
	for i, unique_x in enumerate(order):
	
		df_x = df.loc[df[x] == unique_x]
		
		mean_y = np.mean(df_x[y].tolist())
		#standard_err = stats.sem(df_x[y].tolist())
		standard_err = np.std(df_x[y].tolist())
		
		means[unique_x] = mean_y
		lines[unique_x] = [[i, mean_y-standard_err],[i, mean_y+standard_err]]
		pos[unique_x] = i
		colors_dict[unique_x] = colors[i]
	 
	# Add it to the plot
	for tick, label in zip(pos, ax.get_xticklabels()):
		if colors is not None:
			newline(lines[tick][0], lines[tick][1], color=colors_dict[tick])
			plt.plot(pos[tick], means[tick], marker='D', markersize=3, color=colors_dict[tick])
		else:
			newline(lines[tick][0], lines[tick][1])
			plt.plot(pos[tick], means[tick], marker='D', markersize=3)


def plot_mean_and_sem(df, x, y, order, filename, path_plot_dir, fig_width=None, fig_height=None, colors=None, rotate_x=False, xlabel=None, ylabel=None, ylim=None):
	
	fig, ax = plt.subplots()
	fig.subplots_adjust(left=0.25, right=0.85, top=0.55, bottom=0.25)
	
	plt.xticks(ticks=list(range(len(order))), labels=order)
	
	add_stdev(df, x, y, order, ax, colors=colors)
	
	path_png = os.path.join(path_plot_dir, filename + '.png')
	path_svg = path_png.replace('.png', '.svg')
	
	if xlabel is not None:
		ax.set_xlabel(xlabel)
		
	if ylabel is not None:
		ax.set_ylabel(ylabel)
		
	if ylim is not None:
		ax.set_ylim(ylim)
		
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)
	
	if rotate_x:
		plt.xticks(rotation=45, ha='right')
	
	plt.title(filename)
	plt.show()
	
	if fig_width is not None and fig_height is not None:
		set_size(fig_width, fig_height, ax)
	
	savefig_with_readme(str(sys.argv), inspect.stack(), path_svg)
	savefig_with_readme(str(sys.argv), inspect.stack(), path_png)
	plt.close()

def get_ip_files(path_bam_dirs):

	file_list = []
	for i, path_directory in enumerate(path_bam_dirs):
		rep_name = re.search('run_\d+', path_directory).group(0)	
		rep_num = int(re.search('\d+', rep_name).group(0))
		files = os.listdir(path_directory)
		files = list(filter(bam_file, files))
		files.sort(key=natural_keys)
		paths = [{'path': os.path.join(path_directory, file), 'replicate': rep_num, 'filename': file} for file in files if 'non_ip' not in file]

		file_list += paths

	return file_list

def get_nonip_files(path_bam_dirs):

	file_list = []
	for i, path_directory in enumerate(path_bam_dirs):
		rep_name = re.search('run_\d+', path_directory).group(0)	
		rep_num = int(re.search('\d+', rep_name).group(0))
		files = os.listdir(path_directory)
		files = list(filter(bam_file, files))
		files.sort(key=natural_keys)
		paths = [{'path': os.path.join(path_directory, file), 'replicate': rep_num, 'filename': file} for file in files if 'non_ip' in file]

		file_list += paths

	return file_list

def get_files(path_bam_dirs):

	file_list = []
	for i, path_directory in enumerate(path_bam_dirs):
		rep_name = re.search('run_\d+', path_directory).group(0)	
		rep_num = int(re.search('\d+', rep_name).group(0))
		files = os.listdir(path_directory)
		files = list(filter(bam_file, files))
		files.sort(key=natural_keys)
		paths = [{'path': os.path.join(path_directory, file), 'replicate': rep_num, 'filename': file} for file in files]

		file_list += paths

	return file_list
	
def make_directory(path):
	folder_names = path.split('/')
	full_path = ''
	for folder_name in folder_names:
		full_path = full_path + '/' + folder_name
		if not os.path.isdir(full_path):
			os.mkdir(full_path)
			
	return True
			
def binary_boundary_search(region_boundaries, low, high, insert_midpoint):

	if high > low:

		mid = (high + low) // 2

		if insert_midpoint >= region_boundaries[mid][0] and insert_midpoint <= region_boundaries[mid][1]:
			return mid
		elif insert_midpoint > region_boundaries[mid][1]:
			return binary_boundary_search(region_boundaries, mid + 1, high, insert_midpoint)
		else:
			return binary_boundary_search(region_boundaries, low, mid - 1, insert_midpoint)

	else:

		return -1

def get_feature_files(path_genome_features):
	feature_files = os.listdir(path_genome_features)
	feature_files = list(filter(bed_file, feature_files))
	feature_files.sort(key=natural_keys)
	
	paths = [{'path_feature': os.path.join(path_genome_features, file), 'filename_feature': file} for file in feature_files]
	
	return paths

def create_feature_and_bam_combinations(files, feature_files):
	new_files = []
	for file in files:
		for feature_file in feature_files:
			if 'TSS' in feature_file and 'extend' not in feature_file:
				continue
				
			new_dict = {**file, **feature_file}
			new_files.append(new_dict)
			
	return new_files

def create_dict_entry(input_dict, keys, entry, overwrite=True):
	
	key_to_check = keys.pop(0)
	
	if len(keys) == 0:
		if key_to_check not in input_dict or overwrite:
			input_dict[key_to_check] = entry
	else:
		if key_to_check not in input_dict:
			input_dict[key_to_check] = {}
		input_dict[key_to_check] = create_dict_entry(input_dict[key_to_check], keys, entry, overwrite=overwrite)
	
	return input_dict

def get_best_bandwidth(inserts, np_array_inserts, grid):
	
	if len(inserts) > 2:
		grid.fit(np_array_inserts)
		best_bandwidth = grid.best_estimator_.bandwidth
	else:

		best_bandwidth = 100
		
	return best_bandwidth
