import unittest
import subprocess
# class TestPip(unittest.TestCase):
#     def setUp(self) -> None:
#         self.fasta_paths = "/g/kosinski/geoffrey/alpha-passacaglia/test/test_data/proteins.fasta"
#         self.monomer_object_dir = "/g/kosinski/geoffrey/alphapulldown/test_monomer_objects"
#         self.output_dir = "/g/kosinski/geoffrey/alphapulldown/test_predicted_structures"
#         self.data_dir = "/scratch/AlphaFold_DBs/2.2.0/"
#         self.max_template_date = "2200-01-01"
#         self.oligomer_state_file = "/g/kosinski/geoffrey/alphapulldown/test_homooligomer_state.txt"
#         self.protein_lists = "/g/kosinski/geoffrey/alphapulldown/test_protein_list.txt"
#         self.custom = "/g/kosinski/geoffrey/alphapulldown/test_custom.txt"
#     def test_create_features_no_precomuted_msa(self):
#         exec_cmd = f"create_individual_features.py --fasta_paths={self.fasta_paths} --data_dir={self.data_dir} --output_dir={self.output_dir} --max_template_date={self.max_template_date} --seq_index=2"
#         subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd} --save_msa=True",shell=True,executable="/bin/bash")

    
#     def test_homooligomer(self):
#         exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index=1 --oligomer_state_file={self.oligomer_state_file}"
#         subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")
        
#         exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --oligomer_state_file={self.oligomer_state_file} --data_dir={self.data_dir} --job_index=2"
#         subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")
        
#         exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --oligomer_state_file={self.oligomer_state_file} --job_index=3"
#         subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")

#     def test_all_vs_all(self):
#         for i in [1,2,3]:

#             exec_cmd = f"run_multimer_jobs.py --mode=all_vs_all --output_path={self.output_dir}/all_vs_all --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index={i} --protein_lists={self.protein_lists}"
#             subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")

#     def test_custom(self):
#         for i in [1,2,3]:
#             exec_cmd = f"run_multimer_jobs.py --mode=custom --output_path={self.output_dir}/custom --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index={i} --protein_lists={self.custom}"
#             subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")

# if __name__ == '__main__':
#     unittest.main()
class TestPip:
    def __init__(self) -> None:
        self.fasta_paths = "/g/kosinski/geoffrey/translation_initiation_apms/protein_sequences.fasta"
        self.monomer_object_dir = "/scratch/gyu/test_monomer_objects/test_pip"
        self.output_dir = "/scratch/gyu/test_predicted_structures/test_pip"
        self.data_dir = "/scratch/AlphaFold_DBs/2.2.0/"
        self.max_template_date = "2200-01-01"
        self.oligomer_state_file = "/g/kosinski/geoffrey/alphapulldown/test_homooligomer_state.txt"
        self.protein_lists = "/g/kosinski/geoffrey/alphapulldown/test_protein_list.txt"
        self.custom = "/g/kosinski/geoffrey/alphapulldown/test_custom.txt"
    def test_create_features_no_precomuted_msa(self):
        for i in [3,4,5,6]:
            exec_cmd = f"create_individual_features.py --fasta_paths={self.fasta_paths} --data_dir={self.data_dir} --output_dir={self.monomer_object_dir} --max_template_date={self.max_template_date} --seq_index={i} --skip_existing=True "
            print("will create features first")
            subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd} --save_msa_files=True",shell=True,executable="/bin/bash")

    
    def test_homooligomer(self):
        exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index=1 --oligomer_state_file={self.oligomer_state_file}"
        subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")
        
        exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --oligomer_state_file={self.oligomer_state_file} --data_dir={self.data_dir} --job_index=2"
        subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")
        
        # exec_cmd = f"run_multimer_jobs.py --mode=homo-oligomer --output_path={self.output_dir}/homooligomer --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --oligomer_state_file={self.oligomer_state_file} --job_index=3"
        # subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")

    def test_all_vs_all(self):
        print("now will run test on all_vs_all")
        for i in [1,2]:

            exec_cmd = f"run_multimer_jobs.py --mode=all_vs_all --output_path={self.output_dir}/all_vs_all --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index={i} --protein_lists={self.protein_lists}"
            subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")

    def test_custom(self):
        for i in [1,2]:
            exec_cmd = f"run_multimer_jobs.py --mode=custom --output_path={self.output_dir}/custom --monomer_objects_dir={self.monomer_object_dir} --data_dir={self.data_dir} --job_index={i} --protein_lists={self.custom}"
            subprocess.run(f"module load Anaconda3 && source activate alphapulldown && module load HMMER/3.3.2-gompic-2020b && module load HH-suite/3.3.0-gompic-2020b && {exec_cmd}",shell=True,executable="/bin/bash")
    
    def run_tests(self):
        # self.test_create_features_no_precomuted_msa()
        self.test_homooligomer()
        self.test_all_vs_all()
        self.test_custom()

if __name__ == '__main__':
    test_object = TestPip()
    test_object.run_tests()