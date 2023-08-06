from ..gui_data_selector import Action_on_selector_update
from optimeed.core import ListDataStruct


class On_select_new_trace(Action_on_selector_update):
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
        newStruct = ListDataStruct()
        theData = [the_collection.get_data_at_index(index) for index in selected_data]
        newStruct.set_data(theData)
        selection_identifier = self.theLinkDataGraphs.add_collection(newStruct, {"legend": "{} | {}".format(selection_name, "Selected")})
        self.theLinkDataGraphs.update_graphs()
        
        return selection_identifier

    def cancel_selector(self, selection_identifier):
        self.theLinkDataGraphs.remove_collection(selection_identifier)

    def get_name(self):
        return "Create new trace"
