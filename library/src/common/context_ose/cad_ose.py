# Created by Xinyu Zhu on 10/6/2019, 11:53 PM
import sys

import os

project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)
from common.context_ose.context_operator import ContextOperator


class ContextualAnomalyDetectorOSE(object):
    """
    Contextual Anomaly Detector - Open Source Edition
    2016, Mikhail Smirnov   smirmik@gmail.com
    https://github.com/smirmik/CAD
    """

    def __init__(self,
                 min_value,
                 max_value,
                 base_threshold=0.75,
                 rest_period=30,
                 max_left_semi_contexts_length=7,
                 max_active_neurons_num=15,
                 num_norm_value_bits=3):

        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.rest_period = rest_period
        self.base_threshold = base_threshold
        self.maxActNeurons = max_active_neurons_num
        self.num_norm_value_bits = num_norm_value_bits

        self.max_bin_value = 2 ** self.num_norm_value_bits - 1.0
        self.full_value_range = self.max_value - self.min_value
        if self.full_value_range == 0.0:
            self.full_value_range = self.max_bin_value
        self.min_valueStep = self.full_value_range / self.max_bin_value

        self.left_facts_group = tuple()

        self.context_operator = ContextOperator(max_left_semi_contexts_length)

        self.potential_new_contexts = []

        self.a_scores_history = [1.0]

    def step(self, inp_facts):

        curr_sens_facts = tuple(sorted(set(inp_facts)))

        uniq_pot_new_contexts = set()

        if len(self.left_facts_group) > 0 and len(curr_sens_facts) > 0:
            pot_new_zero_level_context = tuple([self.left_facts_group, curr_sens_facts])
            uniq_pot_new_contexts.add(pot_new_zero_level_context)
            new_context_flag = self.context_operator.get_context_by_facts(
                [pot_new_zero_level_context],
                zerolevel=1
            )
        else:
            new_context_flag = False

        left_crossing = self.context_operator.context_crosser(
            left_or_right=1,
            facts_list=curr_sens_facts,
            new_context_flag=new_context_flag
        )
        active_contexts, num_sel_contexts, pot_new_contexts = left_crossing

        uniq_pot_new_contexts.update(pot_new_contexts)
        num_uniq_pot_new_context = len(uniq_pot_new_contexts)

        if num_sel_contexts > 0:
            percent_selected_context_active = len(active_contexts) / float(num_sel_contexts)
        else:
            percent_selected_context_active = 0.0

        srt_a_contexts = sorted(active_contexts, key=lambda x: (x[1], x[2], x[3]))
        active_neurons = [cInf[0] for cInf in srt_a_contexts[-self.maxActNeurons:]]

        curr_neur_facts = set([2 ** 31 + fact for fact in active_neurons])

        left_facts_group = set()
        left_facts_group.update(curr_sens_facts, curr_neur_facts)
        self.left_facts_group = tuple(sorted(left_facts_group))

        num_new_cont = self.context_operator.context_crosser(
            left_or_right=0,
            facts_list=self.left_facts_group,
            potential_new_contexts=pot_new_contexts
        )

        num_new_cont += 1 if new_context_flag else 0

        if new_context_flag and num_uniq_pot_new_context > 0:
            percent_added_context_to_uniq_pot_new = num_new_cont / float(num_uniq_pot_new_context)
        else:
            percent_added_context_to_uniq_pot_new = 0.0

        return percent_selected_context_active, percent_added_context_to_uniq_pot_new

    def get_anomaly_score(self, input_data):

        norm_inp_val = int(
            (input_data["value"] - self.min_value) / (self.min_valueStep if self.min_valueStep != 0.0 else 0.000001))
        bin_inp_value = bin(norm_inp_val).lstrip("0b").rjust(self.num_norm_value_bits, "0")

        out_sens = []
        for sNum, curr_symb in enumerate(reversed(bin_inp_value)):
            out_sens.append(sNum * 2 + (1 if curr_symb == "1" else 0))
        set_out_sens = set(out_sens)

        anomaly_val1, anomaly_val2 = self.step(set_out_sens)
        current_anomaly_score = (1.0 - anomaly_val1 + anomaly_val2) / 2.0

        if max(self.a_scores_history[-int(self.rest_period):]) < self.base_threshold:
            returned_anomaly_score = current_anomaly_score
        else:
            returned_anomaly_score = 0.0

        self.a_scores_history.append(current_anomaly_score)

        return returned_anomaly_score
