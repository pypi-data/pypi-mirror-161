# https://mybinder.org/
# https://ericmjl.github.io/blog/2020/9/12/add-a-direct-binder-link-for-built-html-notebooks/
# https://mybinder.readthedocs.io/en/latest/examples/sample_repos.html#user-interfaces
# https://github.com/binder-examples/jupyterlab
# ref: Git ref (branch, tag, or commit)
# urlpath=lab/tree/ or labpath=
BINDER_BASE_BADGE: str = "[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/{owner}/{repo}/{ref}?labpath={notebook})"

# https://colab.research.google.com/github/googlecolab/colabtools/blob/master/notebooks/colab-github-demo.ipynb
# https://timsainburg.com/google%20colab.html
COLAB_BASE_BADGE: str = "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/{owner}/{repo}/blob/{ref}/{notebook})"

# https://github.com/SuNaden/deepnote-launch-example
# https://docs.deepnote.com/collaboration/launch-repositories-in-deepnote
DEEPNOTE_BASE_BADGE: str = "[![Deepnote](https://deepnote.com/buttons/launch-in-deepnote-small.svg)](https://deepnote.com/launch?url={url})"
