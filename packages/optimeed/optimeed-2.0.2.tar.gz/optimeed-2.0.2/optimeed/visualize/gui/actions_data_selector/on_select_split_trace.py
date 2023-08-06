from ..gui_data_selector import Action_on_selector_update
from optimeed.core import ListDataStruct


class On_select_split_trace(Action_on_selector_update):
    def __init__(self, theLinkDataGraphs):
        self.theLinkDataGraphs = theLinkDataGraphs
        self.selectedTraces = dict()

    def selector_updated(self, selection_name, the_collection, selected_data, not_selected_data):
        """
        Action to perform once the data have been selected

        :param selection_name: name of the selection (deprecated ?)
        :param the_collection: the collection
        :param selected_data: indices of the data selected
        :param not_selected_data: indices of the data not selected
        :return: identifier that can later be used with cancel_selector
        """
        selections = list()
        for data, name in [(selected_data, "Selected"), (not_selected_data, "Not selected")]:
            newStruct = ListDataStruct()
            theData = [the_collection.get_data_at_index(index) for index in data]
            newStruct.set_data(theData)
            selections.append(self.theLinkDataGraphs.add_collection(newStruct, {"legend": "{} | {}".format(selection_name, name)}))

        self.theLinkDataGraphs.update_graphs()

        return selections

    def cancel_selector(self, selection_identifiers):
        for selection_identifier in selection_identifiers:
            self.theLinkDataGraphs.remove_collection(selection_identifier)

    def get_name(self):
        return "Split trace"
