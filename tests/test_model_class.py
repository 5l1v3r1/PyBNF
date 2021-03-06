from .context import pset
from nose.tools import raises
from os import remove
from os.path import exists
from pybnf.printing import PybnfError

import re


class TestModel:
    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """Define constants to be used in tests"""
        cls.file1 = 'bngl_files/Simple.bngl'
        cls.file2 = 'bngl_files/ParamsEverywhere.bngl'
        cls.file3 = 'bngl_files/Tricky.bngl'
        cls.file4 = 'bngl_files/NFmodel.bngl'
        cls.file5 = 'bngl_files/TrickyWP_p1_5.net'
        cls.file6 = 'bngl_files/Simple_nogen.bngl'

        cls.file1a = 'bngl_files/Simple_Answer.bngl'
        cls.file1b = 'bngl_files/Simple_GenOnly.bngl'
        cls.file1c = 'bngl_files/Simple_AddActions.bngl'

        cls.savefile_prefix = 'bngl_files/NoseTest_Save'
        cls.savefile2_prefix = 'bngl_files/NoseTest_Save2'
        cls.savefile3_prefix = 'bngl_files/NoseTest_Save3'
        cls.savefile4_prefix = 'bngl_files/NoseTest_Save4'
        cls.savefile5_prefix = 'bngl_files/NoseTest_Save5'

        cls.params1 = [
            pset.FreeParameter('kase__FREE', 'normal_var', 0, 1, value=3.8),
            pset.FreeParameter('pase__FREE', 'normal_var', 0, 1, value=0.16),
            pset.FreeParameter('koff__FREE', 'normal_var', 0, 1, value=4.4e-3)
        ]
        cls.params2 = [
            pset.FreeParameter('kase__FREE', 'normal_var', 0, 1, value=3.8),
            pset.FreeParameter('pase__FREE', 'normal_var', 0, 1, value=0.16),
            pset.FreeParameter('wrongname__FREE', 'normal_var', 0, 1, value=4.4e-3)
        ]

    @classmethod
    def teardown_class(cls):
        remove(cls.savefile_prefix + '.bngl')
        remove(cls.savefile2_prefix + '.bngl')
        remove(cls.savefile3_prefix + '.bngl')
        remove(cls.savefile3_prefix + '.net')
        remove(cls.savefile4_prefix + '.bngl')
        remove(cls.savefile4_prefix + '.net')
        remove(cls.savefile5_prefix + '.bngl')

    def test_no_gen_command(self):
        model = pset.BNGLModel(self.file6)
        assert model.generates_network
        assert model.generate_network_line == 'generate_network({overwrite=>1})'

    def test_initialize(self):
        model1 = pset.BNGLModel(self.file1)
        assert model1.param_names == ('kase__FREE', 'koff__FREE', 'pase__FREE')

        model2 = pset.BNGLModel(self.file2)
        assert model2.param_names == (
            'Ag_tot_1__FREE', 'kase__FREE', 'koff__FREE', 'kon__FREE', 'pase__FREE', 't_end__FREE')

        model3 = pset.BNGLModel(self.file3)
        assert model3.param_names == ('__koff2__FREE', 'kase__FREE', 'koff__FREE', 'pase__FREE')

    def test_init_with_pset(self):
        ps1 = pset.PSet(self.params1)
        model1 = pset.BNGLModel(self.file1, ps1)
        assert model1.param_set['kase__FREE'] == 3.8

    @raises(ValueError)
    def test_init_with_pset_error(self):
        ps1 = pset.PSet(self.params2)
        model1 = pset.BNGLModel(self.file1, ps1)
        assert model1.param_set['kase__FREE'] == 3.8

    def test_copy_with_param_set(self):
        model1 = pset.BNGLModel(self.file1)
        ps1 = pset.PSet(self.params1)
        model1b = model1.copy_with_param_set(ps1)
        assert model1b.param_set['kase__FREE'] == 3.8

        nmodel1 = pset.NetModel('TrickyWP_p1_5', [], [], [], nf=self.file5)
        ps1 = pset.PSet([pset.FreeParameter('Nchannel', 'normal_var', 0, 1, value=20)])
        nmodel1b = nmodel1.copy_with_param_set(ps1)
        nmodel1b.save(self.savefile4_prefix)

        with open(self.savefile4_prefix + '.net') as f:
            nmodel1b_lines = f.readlines()

        assert re.search('Nchannel\s+20\s',nmodel1b_lines[6])

    @raises(PybnfError)
    def test_set_param_set_error(self):
        model1 = pset.BNGLModel(self.file1)
        ps2 = pset.PSet(self.params2)
        model1.copy_with_param_set(ps2)

    def test_model_text(self):
        ps1 = pset.PSet(self.params1)
        model1 = pset.BNGLModel(self.file1, ps1)

        f_answer = open(self.file1a)  # File containing the correct output for model_text()
        answer = f_answer.read()
        f_answer.close()
        assert model1.model_text() == answer

    def test_bnglmodel_save(self):
        ps1 = pset.PSet(self.params1)
        model1 = pset.BNGLModel(self.file1, ps1)

        model1.save(self.savefile_prefix)

        f_myguess = open(self.savefile_prefix + '.bngl')
        myguess = f_myguess.read()
        f_myguess.close()

        f_answer = open(self.file1a)  # File containing the correct output for model_text()
        answer = f_answer.read()
        f_answer.close()

        assert myguess == answer

        model1 = pset.BNGLModel(self.file1, ps1)

        model1.save(self.savefile2_prefix, gen_only=True)
        f_myguess2 = open(self.savefile2_prefix + '.bngl')
        myguess2 = f_myguess2.read()
        f_myguess2.close()

        f_answer2 = open(self.file1b)
        answer2 = f_answer2.read()
        f_answer2.close()

        assert myguess2 == answer2

    def test_bngl_config_actions(self):
        ps1 = pset.PSet(self.params1)
        model1 = pset.BNGLModel(self.file1, ps1)
        a1 = pset.TimeCourse({'time': 50, 'step': 10, 'model': 'Simple', 'suffix': 's2'})
        model1.add_action(a1)
        a2 = pset.ParamScan({'min': 10, 'max': 60, 'step': 10, 'time': 5, 'suffix': 's3', 'model': 'Simple',
                             'param': 'kon'})
        model1.add_action(a2)
        model1.save(self.savefile5_prefix)

        f_myguess = open(self.savefile5_prefix + '.bngl')
        myguess = f_myguess.read()
        f_myguess.close()

        f_answer = open(self.file1c)
        answer = f_answer.read()
        f_answer.close()

        assert myguess == answer

    def test_action_suffixes(self):
        m0 = pset.BNGLModel(self.file1)
        assert len(m0.suffixes) == 1
        assert m0.suffixes[0] == ('simulate', 'p1_5')

        m1 = pset.BNGLModel(self.file3)
        assert len(m1.suffixes) == 2
        assert m1.suffixes[1] == ('parameter_scan', 'thing')

    def test_actions(self):
        m0 = pset.BNGLModel(self.file1)
        assert len([a for a in m0.actions if len(a) > 0 and a[0] != '#']) == 2
        for a in m0.actions:
            assert re.search('setOption', a) is None

    def test_network_check(self):
        model0 = pset.BNGLModel(self.file1)
        assert model0.generates_network
        model1 = pset.BNGLModel(self.file4)
        assert not model1.generates_network

    def test_netfile_read(self):
        netmodel = pset.NetModel('TrickyWP_p1_5', [], [], [], nf=self.file5)
        assert len(netmodel.netfile_lines) == 48

    def test_netfile_pcopy_and_save(self):
        netmodel = pset.NetModel('TrickyWP_p1_5', [], [], [], nf=self.file5)
        params = [pset.FreeParameter('Vchannel', 'normal_var', 0, 1, value=1e-5),
                  pset.FreeParameter('H_tot', 'normal_var', 0, 1, value=3.4)]
        ps = pset.PSet(params)
        new_netmodel = netmodel.copy_with_param_set(ps)
        pl0 = new_netmodel.netfile_lines[5]
        pl1 = new_netmodel.netfile_lines[16]
        assert re.search('Vchannel.*1e-05', pl0)
        assert re.search('H_tot.*3.4', pl1)
        for i in range(len(new_netmodel.netfile_lines)):
            if i == 5 or i == 16:
                continue
            else:
                assert new_netmodel.netfile_lines[i] == netmodel.netfile_lines[i]
        new_netmodel.save('bngl_files/NoseTest_Save3')
        assert exists(self.savefile3_prefix + '.net')
        assert exists(self.savefile3_prefix + '.bngl')

        with open(self.savefile3_prefix + '.bngl') as bf:
            bf_lines = bf.readlines()

        assert re.match('readFile', bf_lines[0])



