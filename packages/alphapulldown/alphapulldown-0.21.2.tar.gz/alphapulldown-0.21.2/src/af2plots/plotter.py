import os,sys,re
import pathlib
import glob
import time
import json

import matplotlib.pyplot as plt

import numpy as np
#from iotbx.bioinformatics import any_sequence_format

import pickle
import string
from itertools import groupby

# ------------------------------------------------------
# ------------------------------------------------------
# ------------------------------------------------------
HTML_TEMPLATE="""
<!DOCTYPE html>
<html>
  <body>
  <ul>
    {s.model_info_string}
    <//ul>
    <figure>
        <img src="media/plot_msa.png" alt="MSA" style="width:30%">
        <figcaption>MSA plot</figcaption>
    </figure>

    <figure>
        <img src="media/plot_pae.png" alt="PAE" style="width:30%">
        <figcaption>Predicted Alignment Error plot</figcaption>
    </figure>

    <figure>
        <img src="media/plot_plddt.png" alt="plddt" style="width:30%">
        <figcaption>Predicted lDDT plot</figcaption>
    </figure>

  </body>

</html>
"""

class plotter:


    def __init__(self):
        pass


    # --------------------------------------------------

    def fasta_iter(self, fh):
        """
        by @jkosinski
        Return iterator over FASTA file with multiple sequences.

        Modified from Brent Pedersen
        Correct Way To Parse A Fasta File In Python
        given a fasta file. yield tuples of header, sequence

        :param fh: File Handle to the FASTA file

        :return: 2-element tuple with header and sequence strings
        """

        # ditch the boolean (x[0]) and just keep the header or sequence since
        # we know they alternate.
        faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))

        for header in faiter:
            # drop the ">"
            headerStr = header.__next__()[1:].strip()

            # join all sequence lines to one.
            seq = "".join(s.strip() for s in faiter.__next__())

            yield (headerStr, seq)

    # --------------------------------------------------

    def msa2fig(self, a3m_filenames, num_cols=3, chain_descr_dict=None, dpi=100):

        def parse_msa(msa):
            query_sequence = msa[0]
            seq_len = len(query_sequence)
            lines = []

            chain_seq = np.array(list(query_sequence[:seq_len]))
            chain_msa = np.array([_[:seq_len] for _ in msa])
            seqid = np.array([np.count_nonzero(np.array(chain_seq) == msa_line[:seq_len])/len(chain_seq) for msa_line in msa])
            non_gaps = (chain_msa != '-').astype(float)

            non_gaps[non_gaps == 0] = np.nan

            # order by decreasing sequence identity
            new_order = np.argsort(seqid, axis=0)[::-1]
            lines.append( (non_gaps[:] * seqid[:, None])[new_order] )

            lines = np.concatenate(lines, 1)
            return lines

        # --------------------------------------------------

        if not isinstance(a3m_filenames, list):
            a3m_filenames = [a3m_filenames]

        lowcase_table = str.maketrans('', '', string.ascii_lowercase)

        msas = []
        for fn in a3m_filenames:
            chid = os.path.dirname(fn).split('/')[-1]
            print(fn)
            with open(fn, 'r') as ifile:
                #_msa, err = any_sequence_format(file_name="weird.fasta", data=ifile.read())
                _msa = self.fasta_iter(fh=ifile.readlines())

            #print("# sequences in MSA %s " % os.path.basename(fn),len(_msa)  )
            if chain_descr_dict:
                #msas.append( (chain_descr_dict[chid].get('description', 'UNK'), np.array([list(_.sequence.strip()) for _ in _msa],dtype=object)) )
                msas.append( (chain_descr_dict[chid].get('description', 'UNK'), np.array([list(_[1].strip().translate(lowcase_table)) for _ in _msa],dtype=object)) )
            else:
                #msas.append( ('UNK', np.array([list(_.sequence.strip()) for _ in _msa],dtype=object)) )
                msas.append( ('UNK', np.array([list(_[1].strip().translate(lowcase_table)) for _ in _msa],dtype=object)) )

        # plotting stuff
        num_cols = min(num_cols,len(msas))
        num_rows = int(np.ceil(len(msas)/num_cols))

        fig = plt.figure(figsize=(6 * num_cols, 4*(num_rows)), dpi=dpi)
        fig.subplots_adjust(bottom=0.15, left=.15, right=.9, top=.9, wspace=.3, hspace=0.4)

        for idx, (name,msa) in enumerate(msas):

            ax = fig.add_subplot(num_rows, num_cols, idx + 1)

            lines = parse_msa(msa)

            ax.set_title("Sequence coverage\n%s"%name)
            im = ax.imshow(
                    lines[::-1],
                    interpolation="nearest",
                    aspect="auto",
                    cmap="rainbow_r",
                    vmin=0,
                    vmax=1,
                    origin="lower",
                    extent=(0, lines.shape[1], 0, lines.shape[0]))

            ax.plot((np.isnan(lines) == False).sum(0), color="black")
            ax.set_xlim(0, lines.shape[1])
            ax.set_ylim(0, lines.shape[0])

            ax.set_xlabel("Residue number")
            ax.set_ylabel("Sequences")

            fig.colorbar(im, ax=ax, label="Sequence identity to query")

        fig.tight_layout()

        return fig

    # ------------------------------------------------------

    def parse_model_pickles(self, datadir):

        datadict = {}

        for fn in glob.glob("%s/result*.pkl" % datadir):
            #m=re.match(r".*result\_model\_(?P<idx>\d+)\_multimer\.pkl", fn)
            m=re.match(r".*result(?P<jobid>\_[\w\d]+)?\_model\_(?P<idx>\d+)(\_\w+)?\.pkl", fn)
            with open(fn, 'rb') as ifile:
                data = pickle.load(ifile)

                # ptm - ranking_confidence, it's (?) predicted_tm_score in openFold

                if 'ptm' in data:
                    ptm = float(data['ptm'])

                    #elif 'predicted_tm_score' in data:
                    #ptm = float(data['predicted_tm_score'])
                elif 'ranking_confidence' in data:
                    ptm = float(data['ranking_confidence'])
                else:
                    ptm = np.mean(data['plddt'], dtype=float)

                datadict[fn] = {'datadir':datadir,
                                'fn':fn,
                                'idx':int(m.group('idx')),
                                'ptm':ptm,
                                'pae':data['predicted_aligned_error'] if 'predicted_aligned_error' in data else None,
                                'plddt':data['plddt']}
        assert datadict
        for rank,k in enumerate(sorted(datadict, key=lambda x:datadict[x]['ptm'], reverse=True)):
            datadict[k]['rank']=rank+1
            datadict[k]['description'] = "rank_%i %s pLDDT=%.2f" % (rank, os.path.basename(k), datadict[k]['ptm'])
            print(datadict[k]['description'])

        return datadict

    # ------------------------------------------------------

    def plot_predicted_alignment_error(self, datadict, num_cols=6, dpi=100):
        n_models = len(datadict)
        #plt.figure(figsize=(3 * n_models, 2), dpi=100)
        #fig = plt.figure(figsize=(3 * n_models, 2), dpi=dpi)


        # plotting stuff
        num_cols = min(num_cols,n_models)
        num_rows = int(np.ceil(n_models/num_cols))

        fig = plt.figure(figsize=(6 * num_cols, 4*(num_rows)), dpi=dpi)


        fig.subplots_adjust(bottom=0.1, left=.01, right=.99, top=.9, wspace=.2, hspace=0.3)

        for idx,k in enumerate(sorted(datadict, key=lambda x:datadict[x]['rank'])):
            #plt.subplot(1, n_models, idx + 1)
            #ax = fig.add_subplot(1, n_models, idx + 1)
            ax = fig.add_subplot(num_rows, num_cols, idx + 1)

            ax.set_title("#%i: model_%i" % (datadict[k]['rank'], datadict[k]['idx']) )
            im=ax.imshow(datadict[k]['pae'], label=str(idx+1), cmap="bwr", vmin=0, vmax=30)
            fig.colorbar(im, ax=ax, label="$[\AA]$")
        fig.tight_layout()
        return fig
        #plt.show()

    # ------------------------------------------------------

    def plot_plddts(self, datadict, Ls=None, dpi=100, fig=True):
        #plt.figure(figsize=(6,4),dpi=100)
        fig = plt.figure(figsize=(6,4), dpi=dpi)

        ax = fig.add_subplot(1,1,1)
        ax.set_title("Predicted lDDT per residue")

        for idx,k in enumerate(sorted(datadict, key=lambda x:datadict[x]['rank'])):
            ax.plot(datadict[k]['plddt'],label='' if idx>5 else "#%i: model_%i" % (datadict[k]['rank'], datadict[k]['idx']))

        ax.legend()
        ax.set_ylim(0,100)
        ax.set_ylabel("Predicted lDDT")
        ax.set_xlabel("Residue number")

        fig.tight_layout()

        return fig

    # ------------------------------------------------------

    def parse_all_fig_data(self, pkl_dir):
        fig_dict = {}

        # PAE plot object
        self.datadict= self.parse_model_pickles(pkl_dir)
        ff=self.plot_predicted_alignment_error(self.datadict)
        fig_dict['pae'] = ff

        # plddt plot object (only top5 curves are labelled)
        ff=self.plot_plddts(self.datadict)
        fig_dict['plddt'] = ff

        # this wil try to plot MSA too
        fns=[]
        for dirname,_,_ in os.walk(pkl_dir):
            _fn = glob.glob("%s/bfd*.a3m" % dirname)
            if _fn: fns.extend(_fn)

        if fns:
            ff = self.msa2fig(a3m_filenames=fns)
            fig_dict['msa'] = ff


        return fig_dict

    # ------------------------------------------------------

    def make_output_directory(self, output):
        output_dir=os.path.expanduser(output)

        try:
            pathlib.Path(output_dir).mkdir(parents=True, exist_ok=False)
        except:
            print("*** ERROR: output directory already exists: %s\n" % output_dir)
            return None

        print("Created output directory: ", output_dir)
        return output_dir

    # ------------------------------------------------------

    def make_html_report(self, pkl_dir, html_out):

        self.make_output_directory(html_out)
        media_dir = os.path.join(html_out, 'media')
        self.make_output_directory(media_dir)

        fig_dict = self.parse_all_fig_data(pkl_dir)
        for suffix, ff in fig_dict.items():
            ofn = os.path.join(media_dir, f"plot_{suffix}.png")
            ff.savefig(ofn)
            print(f'Wrote {ofn}')


        model_info=[]
        for idx,k in enumerate(sorted(self.datadict, key=lambda x:self.datadict[x]['rank'])):
            model_info.append("<li>%s</li>"%self.datadict[k]['description'])

        self.model_info_string="\n".join(model_info)

        with open( os.path.join(html_out, 'report.html'), 'w' ) as ofile:
            ofile.write(HTML_TEMPLATE.format(s=self))


        print("Write HTML report to: ", os.path.join(html_out, 'report.html'))


# ------------------------------------------------------
# ------------------------------------------------------
# ------------------------------------------------------
