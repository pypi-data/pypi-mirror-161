""".. versionadded:: 0.0.1

Control the macOS TextEdit application using JXA-like syntax.
"""
import iTunesLibrary
import MediaPlayer
from typing import List, Union
from AppKit import NSFileManager, NSURL, NSSet

from AppKit import NSPredicate, NSMutableArray

from PyXA import XABase
from PyXA import XABaseScriptable

_KIND_UNKNOWN = iTunesLibrary.ITLibMediaItemMediaKindUnknown
_KIND_PODCAST = iTunesLibrary.ITLibMediaItemMediaKindPodcast

class XAPodcastsApplication(XABase.XAApplication):
    """A class for managing and interacting with Podcasts.app.

    .. seealso:: :class:`XATextEditWindow`, :class:`XATextEditDocument`

    .. versionadded:: 0.0.1
    """
    def __init__(self, properties):
        super().__init__(properties)
        self.xa_ilib = iTunesLibrary.ITLibrary.alloc().initWithAPIVersion_error_("1.0", None)[0]
        self.xa_mlib = MediaPlayer.MPMediaLibrary.defaultMediaLibrary()
        self.xa_trax = self.xa_ilib.allMediaItems()

    # Podcasts
    def podcasts(self, filter: dict = None) -> List['XAPodcast']:
        """Returns a list of documents matching the filter.

        .. seealso:: :func:`scriptable_elements`

        .. versionadded:: 0.0.1
        """
        predicate = MediaPlayer.MPMediaPropertyPredicate.alloc().init()
        #predicate.setValue_(MediaPlayer.MPMediaTypePodcast)
        predicate.setValue_(MediaPlayer.MPMediaTypeTVShow)
        predicate.setProperty_("mediaType")
        predicate.setComparisonType_(MediaPlayer.MPMediaPredicateComparisonEqualTo)

        print(predicate)
        query = MediaPlayer.MPMediaQuery.alloc().init()
        query.addFilterPredicate_(predicate)
        
        print(query.items())
        # self.xa_ilib.reloadData()
        # media_items = self.xa_ilib.allMediaItems()
        # podcast_filter = [
        #     ("mediaKind", _KIND_PODCAST),
        #     ("mediaKind", _KIND_UNKNOWN)
        # ]
        # print(XABase.xa_or_predicate_format(podcast_filter))
        # predicate = NSPredicate.predicateWithFormat_(XABase.xa_or_predicate_format(podcast_filter))
        # podcasts = media_items.filteredArrayUsingPredicate_(predicate)
        
        # for item in media_items:
        #     print(item.title(), item.mediaKind())

class XAPodcast(XABaseScriptable.XASBPrintable):
    """A class for managing and interacting with TextEdit documents.

    .. seealso:: :class:`XATextEditApplication`

    .. versionadded:: 0.0.1
    """
    def __init__(self, properties):
        super().__init__(properties)