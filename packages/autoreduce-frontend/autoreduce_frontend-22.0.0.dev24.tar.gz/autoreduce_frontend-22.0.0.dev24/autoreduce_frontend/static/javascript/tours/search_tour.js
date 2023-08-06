steps = [
    {
        element: "#id_run_number",
        title: "Filter: Run Number",
        content: "Enter a run number to search for. A range can be entered (e.g. 60180-60190), Specific runs can be entered (e.g. 60180,60190)",
        placement: "top"
    },
    {
        element: "#id_instrument",
        title: "Filter: Instrument",
        content: "Select an Instrument to filter on from this dropdown menu.",
        placement: "top"
    },
    {
        element: "#id_run_description",
        title: "Filter: Run Description",
        content: "Enter text here to filter by a run's description.",
        placement: "top"
    },
    {
        element: "#contains",
        title: "Filter: Run Description",
        content: "Select this button to find runs that contain the text in the run description textbox.",
        placement: "top"
    },
    {
        element: "#exact",
        title: "Filter: Instrument",
        content: "Select this button to find runs that contain the exact text in the run description textbox.",
        placement: "top"
    },
];
if (typeof tourSteps == 'undefined') {
    tourSteps = steps
}
else {
    tourSteps = tourSteps.concat(steps)
}
