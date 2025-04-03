from DirectoryTreeCreator import DirectoryTreeCreator

networkMap = [dict({
        'url': "www.google.com",
        'path': "/",
        'children': [
            {
                'url': "www.google.com/search",
                'path': "/search",
                'children': [
                    {
                        'url': "www.google.com/search/search",
                        'path': "/search/search",
                        'children': []
                    }
                ]
            },
            {
                'url': "www.google.com/earth",
                'path': "/earth",
                'children': [
                    {
                        'url': "www.google.com/earth/search",
                        'path': "/earth/search",
                        'children': [
                            
                        ]
                    }
                ]
            }
        ]
    })]

treeCreator = DirectoryTreeCreator()
treeCreator.populate(networkMap)
treeCreator.add_edge(('www.google.com','/'), ('linked-in.com','/l'))
treeCreator.add_edge(('linked-in.com','/l'), ('random.com','/rnd'))
treeCreator.add_edge(('www.google.com','/'), ('random.com','/rnd'))
treeCreator.display_pretty(treeCreator.tree.root)