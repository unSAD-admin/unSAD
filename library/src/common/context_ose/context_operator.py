# Created by Xinyu Zhu on 10/6/2019, 11:52 PM
# ----------------------------------------------------------------------
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

class ContextOperator:
    """
    Contextual Anomaly Detector - Open Source Edition
    2016, Mikhail Smirnov   smirmik@gmail.com
    https://github.com/smirmik/CAD
    """

    def __init__(self, max_left_semi_contexts_length):

        self.max_left_semi_contexts_length = max_left_semi_contexts_length

        self.facts_dics = [{}, {}]
        self.semi_context_dics = [{}, {}]
        self.semi_cont_val_lists = [[], []]
        self.crossed_semi_contexts_lists = [[], []]
        self.contexts_values_list = []

        self.new_context_id = False

    def getContextByFacts(self, new_contexts_list, zerolevel=0):
        """
        The function which determines by the complete facts list whether the
        context is already saved to the memory. If the context is not found the
        function immediately creates such. To optimize speed and volume of the
        occupied memory the contexts are divided into semi-contexts as several
        contexts can contain the same facts set in its left and right parts.
        @param new_contexts_list:     list of potentially new contexts
        @param zerolevel:         flag indicating the context type in
                        transmitted list
        @return : depending on the type of  potentially new context transmitted as
              an input parameters the function returns either:
              a) flag indicating that the transmitted zero-level context is
              a new/existing one;
              or:
              b) number of the really new contexts that have been saved to the
              context memory.
        """

        num_added_contexts = 0

        for leftFacts, rightFacts in new_contexts_list:

            left_hash = leftFacts.__hash__()
            right_hash = rightFacts.__hash__()

            next_left_semi_context_number = len(self.semi_context_dics[0])
            left_semi_context_id = self.semi_context_dics[0].setdefault(
                left_hash,
                next_left_semi_context_number
            )
            if left_semi_context_id == next_left_semi_context_number:
                left_semi_cont_val = [[], len(leftFacts), 0, {}]
                self.semi_cont_val_lists[0].append(left_semi_cont_val)
                for fact in leftFacts:
                    semi_context_list = self.facts_dics[0].setdefault(fact, [])
                    semi_context_list.append(left_semi_cont_val)

            next_right_semi_context_number = len(self.semi_context_dics[1])
            right_semi_context_id = self.semi_context_dics[1].setdefault(
                right_hash,
                next_right_semi_context_number
            )
            if right_semi_context_id == next_right_semi_context_number:
                right_semi_context_values = [[], len(rightFacts), 0]
                self.semi_cont_val_lists[1].append(right_semi_context_values)
                for fact in rightFacts:
                    semi_context_list = self.facts_dics[1].setdefault(fact, [])
                    semi_context_list.append(right_semi_context_values)

            next_free_context_id_number = len(self.contexts_values_list)
            context_id = self.semi_cont_val_lists[0][left_semi_context_id][3].setdefault(
                right_semi_context_id,
                next_free_context_id_number
            )

            if context_id == next_free_context_id_number:
                num_added_contexts += 1
                context_values = [0, zerolevel, left_hash, right_hash]

                self.contexts_values_list.append(context_values)
                if zerolevel:
                    self.new_context_id = context_id
                    return True
            else:
                context_values = self.contexts_values_list[context_id]

                if zerolevel:
                    context_values[1] = 1
                    return False

        return num_added_contexts

    def contextCrosser(self,
                       left_or_right,
                       facts_list,
                       new_context_flag=False,
                       potential_new_contexts=None):

        if left_or_right == 0:
            if len(potential_new_contexts) > 0:
                num_new_contexts = self.getContextByFacts(potential_new_contexts)
            else:
                num_new_contexts = 0

        for semiContextValues in self.crossed_semi_contexts_lists[left_or_right]:
            semiContextValues[0] = []
            semiContextValues[2] = 0

        for fact in facts_list:
            for semiContextValues in self.facts_dics[left_or_right].get(fact, []):
                semiContextValues[0].append(fact)

        new_crossed_values = []

        for semiContextValues in self.semi_cont_val_lists[left_or_right]:
            len_semi_context_values0 = len(semiContextValues[0])
            semiContextValues[2] = len_semi_context_values0
            if len_semi_context_values0 > 0:
                new_crossed_values.append(semiContextValues)

        self.crossed_semi_contexts_lists[left_or_right] = new_crossed_values

        if left_or_right:
            return self.updateContextsAndGetActive(new_context_flag)

        else:
            return num_new_contexts

    def updateContextsAndGetActive(self, new_context_flag):
        """
        This function reviews the list of previously selected left semi-contexts,
        creates the list of potentially new contexts resulted from intersection
        between zero-level contexts, determines the contexts that coincide with
        the input data and require activation.
        @param new_context_flag:     flag indicating that a new zero-level
                        context is not recorded at the current
                        step, which means that all contexts
                        already exist and there is no need to
                        create new ones.
        @return active_contexts:     list of identifiers of the contexts which
                        completely coincide with the input stream,
                        should be considered active and be
                        recorded to the input stream of "neurons"
        @return potentialNewContextsLists:  list of contexts based on intersection
                        between the left and the right zero-level
                        semi-contexts, which are potentially new
                        contexts requiring saving to the context
                        memory
        """

        active_contexts = []
        num_selected_context = 0

        potential_new_contexts = []

        for leftSemiContVal in self.crossed_semi_contexts_lists[0]:

            for rightSemiContextID, contextID in leftSemiContVal[3].items():

                if self.new_context_id != contextID:

                    context_values = self.contexts_values_list[contextID]
                    right_semi_cont_val = self.semi_cont_val_lists[1][rightSemiContextID]
                    right_sem_con_val0, right_sem_con_val1, right_sem_con_val2 = right_semi_cont_val

                    if leftSemiContVal[1] == leftSemiContVal[2]:

                        num_selected_context += 1

                        if right_sem_con_val2 > 0:

                            if right_sem_con_val1 == right_sem_con_val2:
                                context_values[0] += 1
                                active_contexts.append([contextID,
                                                        context_values[0],
                                                        context_values[2],
                                                        context_values[3]
                                                        ])

                            elif context_values[1] and new_context_flag:
                                if leftSemiContVal[2] <= self.max_left_semi_contexts_length:
                                    left_facts = tuple(leftSemiContVal[0])
                                    right_facts = tuple(right_sem_con_val0)
                                    potential_new_contexts.append(tuple([left_facts, right_facts]))

                    elif context_values[1] and new_context_flag and right_sem_con_val2 > 0:
                        if leftSemiContVal[2] <= self.max_left_semi_contexts_length:
                            left_facts = tuple(leftSemiContVal[0])
                            right_facts = tuple(right_sem_con_val0)
                            potential_new_contexts.append(tuple([left_facts, right_facts]))

        self.new_context_id = False

        return active_contexts, num_selected_context, potential_new_contexts
