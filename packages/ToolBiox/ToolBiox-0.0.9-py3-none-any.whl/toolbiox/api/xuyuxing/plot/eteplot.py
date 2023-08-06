def draw_tree_to_file(tree, tree_style, output_file):
    from pyvirtualdisplay import Display

    display = Display(visible=False, color_depth=24)
    display.start()

    print(output_file)
    tree.render(output_file, tree_style=tree_style)
    # t.show(tree_style=ts)

    display.stop()
