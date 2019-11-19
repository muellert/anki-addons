# -*- mode: Python ; coding: utf-8 -*-
#
# © 2013–2018  Roland Sieker <ospalh@gmail.com>
# © 2017 Marcio Mazza
#
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Images:
#
# most icons from Anki1
#
# Exceptions:
# study.png,
# Found at http://www.vectorarts.net/vector-icons/free-study-book-icons/ ,
# "Free for Personal and Commercial Use"
#
# A few others, notably the 'bury', 'suspend', 'options', 'record' and
# 'play recorded' icons were found at openclipart.org:
# Free: http://creativecommons.org/publicdomain/zero/1.0/
#
# Others from other “public domain” images libraries.


"""
Add standard tool bars to Anki 2.1.

This Anki 2.1 addon adds standard tool bars (QtToolBar) to the Anki
main window. By default a few buttons (QActions) are added, more can
be added by the user.
"""

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QAction, QMenu, QToolBar
import os

from anki.hooks import wrap, addHook
from anki.lang import _
from aqt import mw, clayout
from aqt.deckbrowser import DeckBrowser
from aqt.overview import Overview
from aqt.reviewer import Reviewer
from aqt.utils import askUser


__version__ = "1.5.0"


config = mw.addonManager.getConfig(__name__)
#todo: show edit layout
#todo: hide study options gear

icons_dir = os.path.join(
    mw.pm.addonFolder(), 'colorful_toolbars', 'color_icons')


toolbar_gradient_form = u'''QToolBar:top, QToolBar:bottom {{
background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg}, stop:1 {bgg});
}}
QToolBar:left, QToolBar:right {{
background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {bg}, stop:1 {bgg});
}}
QToolBar:top {{border-bottom: 1px solid {bgl};}}
QToolBar:bottom {{border-top: 1px solid {bgl};}}
QToolBar:left {{border-right: 1px solid {bgl};}}
QToolBar:right {{border-left: 1px solid {bgl};}} '''


def go_deck_browse():
    """Open the deck browser."""
    mw.moveToState("deckBrowser")


def go_study():
    """Start studying cards."""
    mw.col.reset()
    mw.col.startTimebox()
    mw.moveToState("review")


def go_edit_current():
    """Edit the current card when there is one."""
    try:
        mw.onEditCurrent()
    except AttributeError:
        pass


def go_edit_layout():
    """Edit the current card's note's layout if there is one."""
    try:
        ccard = mw.reviewer.card
        clayout.CardLayout(mw, ccard.note(), ord=ccard.ord)
    except AttributeError:
        return


def toggle_text_toolbar():
    """Switch the original toolbar on or off."""
    if show_text_toolbar_action.isChecked():
        mw.toolbar.web.show()
    else:
        mw.toolbar.web.hide()


def toggle_qt_toolbar():
    """Switch the new upper tool bar on or off."""
    if show_qt_toolbar_action.isChecked():
        mw.qt_toolbar.show()
    else:
        mw.qt_toolbar.hide()


def toggle_more_toolbar():
    """Switch the new lower tool bar on or off."""
    # No real need to check if we are in review. Only then should we
    # be able to activate the action.
    if show_more_toolbar_action.isChecked():
        mw.reviewer.more_toolbar.show()
    else:
        mw.reviewer.more_toolbar.hide()


def ask_delete():
    """Delete a note after asking the user."""
    if askUser('Delete note?', defaultno=True):
        mw.reviewer.onDelete()


def add_toolbar():
    """
    Add a Qt tool bar to Anki2.

    This is a more Anki-1-ish Qt tool bar with a number of rather big,
    colorful icons to replace the Anki 2 DSAB toolbar.
    """
    mw.qt_toolbar = QToolBar()
    # mw.qt_toolbar.setAccessibleName('secondary tool bar')
    mw.qt_toolbar.setObjectName('qt tool bar')
    mw.qt_toolbar.setIconSize(QSize(32, 32))
    # Conditional setup
    mw.qt_toolbar.setFloatable(True)
    mw.qt_toolbar.setMovable(True)
    mw.addToolBar(Qt.TopToolBarArea, mw.qt_toolbar)
    palette = mw.qt_toolbar.palette()
    fg = palette.color(QPalette.ButtonText)
    bg = palette.color(QPalette.Button)
    if bg.lightnessF() > fg.lightnessF():
        bgg = bg.darker(108)
        bgl = bg.darker()
    else:
        bgg = bg.lighter(120)
        bgl = bg.lighter()
    mw.qt_toolbar.setStyleSheet(
        toolbar_gradient_form.format(
            bg=bg.name(), bgg=bgg.name(), bgl=bgl.name()))
    # Add the actions here
    mw.qt_toolbar.addAction(sync_action)
    # Put this in the more tool bar, closer to the old edit button
    #    mw.qt_toolbar.addAction(edit_current_action)
    mw.qt_toolbar.addAction(decks_action)
    mw.qt_toolbar.addAction(overview_action)
    # Keep in line with the old tool bar. Don't show in standard version.
    # mw.qt_toolbar.addAction(study_action)
    mw.qt_toolbar.addAction(add_notes_action)
    mw.qt_toolbar.addAction(browse_cards_action)
    mw.qt_toolbar.addAction(statistics_action)


def add_more_toolbar():
    """
    Add a tool bar at the bottom.

    This provieds colorful command buttons for the functions usually
    hidden in the "More" button at the bottom.
    """
    try:
        mw.reviewer.more_toolbar = QToolBar()
    except AttributeError:
        return
    # mw.reviewer.more_toolbar.setAccessibleName('secondary tool bar')
    mw.reviewer.more_toolbar.setObjectName('more options tool bar')
    mw.reviewer.more_toolbar.setIconSize(QSize(24, 24))
    mw.reviewer.more_toolbar.setFloatable(False)
    mw.reviewer.more_toolbar.setMovable(False)
    mw.mainLayout.insertWidget(2, mw.reviewer.more_toolbar)
    palette = mw.reviewer.more_toolbar.palette()
    fg = palette.color(QPalette.ButtonText)
    bg = palette.color(QPalette.Button)
    if bg.lightnessF() > fg.lightnessF():
        bgg = bg.darker(108)
        bgl = bg.darker()
    else:
        bgg = bg.lighter(105)
        bgl = bg.lighter()
    mw.reviewer.more_toolbar.setStyleSheet(
        toolbar_gradient_form.format(
            bg=bg.name(), bgg=bgg.name(), bgl=bgl.name()))
    # Add the actions here
    mw.reviewer.more_toolbar.addAction(edit_current_action)
    if config["show_edit_layout"]:
        mw.reviewer.more_toolbar.addAction(edit_layout_action)
    mw.reviewer.more_toolbar.addSeparator()
    mw.reviewer.more_toolbar.addAction(toggle_mark_action)
    if config["show_last_card"]:
        mw.reviewer.more_toolbar.addAction(toggle_last_card_action)
    if config["show_mute_button"]:
        mw.reviewer.more_toolbar.addAction(mute_action)
    mw.reviewer.more_toolbar.addAction(bury_action)
    if config["show_suspend_card"]:
        mw.reviewer.more_toolbar.addAction(suspend_card_action)
    if config["show_suspend_note"]:
        mw.reviewer.more_toolbar.addAction(suspend_note_action)
    if config["show_delete_note"]:
        mw.reviewer.more_toolbar.addAction(delete_action)
    if config["show_undo"]:
        mw.reviewer.more_toolbar.addAction(mw.form.actionUndo)
    if config["show_options_button"]:
        mw.reviewer.more_toolbar.addSeparator()
        mw.reviewer.more_toolbar.addAction(options_action)
    mw.reviewer.more_toolbar.addSeparator()
    mw.reviewer.more_toolbar.addAction(replay_action)
    if config["show_voice_buttons"]:
        mw.reviewer.more_toolbar.addAction(record_own_action)
        mw.reviewer.more_toolbar.addAction(replay_own_action)
    more_toolbar_off()


def add_to_menus():
    """
    Add a number of items to memus.

    Put the functions of the DASB old-style tool bar links into
    menus. Sync to the file menu, stats to the tools menu, the DASB,
    together with a study-withouts-overview item to a new go
    menu. Also add items to, d'uh, edit stuff to the edit menu.

    """
    # Add sync to the file memu. It was there in Anki 1.
    mw.form.menuCol.insertAction(mw.form.actionImport, sync_action)
    # Make a new top level menu and insert it.
    try:
        mw.addon_view_menu.addSeparator()
    except AttributeError:
        mw.addon_view_menu = QMenu(_(u"&View"), mw)
        mw.form.menubar.insertMenu(
            mw.form.menuTools.menuAction(), mw.addon_view_menu)
    mw.addon_view_menu.addAction(show_qt_toolbar_action)
    mw.addon_view_menu.addAction(show_text_toolbar_action)
    mw.addon_view_menu.addAction(show_more_toolbar_action)
    # And another one
    try:
        mw.addon_go_menu.addSeparator()
    except AttributeError:
        mw.addon_go_menu = QMenu(_(u"&Go"), mw)
        mw.form.menubar.insertMenu(
            mw.form.menuTools.menuAction(), mw.addon_go_menu)
    # Add DSAB to the new go menu
    mw.addon_go_menu.addAction(decks_action)
    mw.addon_go_menu.addAction(overview_action)
    mw.addon_go_menu.addAction(study_action)
    mw.addon_go_menu.addAction(add_notes_action)
    mw.addon_go_menu.addAction(browse_cards_action)
    mw.addon_go_menu.addAction(toggle_last_card_action)
    mw.addon_view_menu.addAction(mute_action)
    # Stats. Maybe this should go to help. Seems somewhat help-ish to
    # me, but not too much.
    mw.form.menuTools.addAction(statistics_action)
    # Add to the edit menu. The undo looked a bit forlorn.
    edit_menu = mw.form.menuEdit
    edit_menu.addSeparator()
    edit_menu.addAction(edit_current_action)
    edit_menu.addAction(edit_layout_action)
    edit_menu.addSeparator()
    edit_menu.addAction(bury_action)
    edit_menu.addAction(toggle_mark_action)
    edit_menu.addAction(suspend_card_action)
    edit_menu.addAction(suspend_note_action)
    edit_menu.addAction(delete_action)


def edit_actions_off():
    """Switch off the edit actions."""
    try:
        edit_current_action.setEnabled(False)
        edit_layout_action.setEnabled(False)
        bury_action.setEnabled(False)
        toggle_mark_action.setEnabled(False)
        suspend_card_action.setEnabled(False)
        suspend_note_action.setEnabled(False)
        delete_action.setEnabled(False)
    except AttributeError:
        pass


def edit_actions_on():
    """Switch on the edit actions."""
    try:
        edit_current_action.setEnabled(True)
        edit_layout_action.setEnabled(True)
    except AttributeError:
        pass


def more_toolbar_off():
    """Hide the more tool bar."""
    show_more_toolbar_action.setEnabled(False)
    bury_action.setEnabled(False)
    toggle_mark_action.setEnabled(False)
    suspend_card_action.setEnabled(False)
    suspend_note_action.setEnabled(False)
    delete_action.setEnabled(False)
    try:
        mw.reviewer.more_toolbar.hide()
    except AttributeError:
        pass


def maybe_more_toolbar_on():
    show_more_toolbar_action.setEnabled(True)
    bury_action.setEnabled(True)
    toggle_mark_action.setEnabled(True)
    suspend_card_action.setEnabled(True)
    suspend_note_action.setEnabled(True)
    delete_action.setEnabled(True)
    if show_more_toolbar_action.isChecked():
        try:
            mw.reviewer.more_toolbar.show()
        except AttributeError:
            pass


def save_toolbars_visible():
    """Save if we should show the tool bars in the profile."""
    mw.pm.profile['ctb_show_toolbar'] = show_text_toolbar_action.isChecked()
    mw.pm.profile['ctb_show_qt_toolbar'] = show_qt_toolbar_action.isChecked()
    mw.pm.profile['ctb_show_more_toolbar'] = \
        show_more_toolbar_action.isChecked()


def load_toolbars_visible():
    """
    Show the right tool bars.

    Get the state if we should show the tool bars from the profile or
    use default values. Then show or do not show those tool bars.
    """
    try:
        ttb_on = mw.pm.profile['ctb_show_toolbar']
    except KeyError:
        ttb_on = False
    show_text_toolbar_action.setChecked(ttb_on)
    toggle_text_toolbar()
    try:
        qtb_on = mw.pm.profile['ctb_show_qt_toolbar']
    except KeyError:
        qtb_on = True
    show_qt_toolbar_action.setChecked(qtb_on)
    toggle_qt_toolbar()
    try:
        mtb_on = mw.pm.profile['ctb_show_more_toolbar']
    except KeyError:
        mtb_on = True
    show_more_toolbar_action.setChecked(mtb_on)
    # Don't toggle the more tool bar yet. It would be shown on the
    # deck browser screen
    # toggle_more_toolbar()


def update_mark_action():
    """Set the state of the mark action to the marked state of the note."""
    toggle_mark_action.setChecked(mw.reviewer.card.note().hasTag("marked"))


def next_card_wrapper(self):
    u"""Go to the deck overview or show the next card."""
    if toggle_last_card_action.isChecked():
        self.mw.moveToState("overview")
        toggle_last_card_action.setChecked(False)
    else:
        original_next_card(self)


def next_card_toggle_off():
    """Switch the next card action off."""
    toggle_last_card_action.setChecked(False)


def maybe_autoplay(reviewer, card):
    u"""
    Return whether we should play the sound on card flips.

    Return False when we have swiched on mute, the standard autoplay
    state otherwise.
    """
    if mute_action.isChecked():
        return False
    return reviewer.mw.col.decks.confForDid(card.odid or card.did)['autoplay']


# Make all the actions top level, so we can use them for the menu and
# the tool bar.

# Most of the icons are part of the standard version, but as they are
# not currently used by the standard version, they may disappear when
# dae gets around to doing some clean up. So bring them along, anyway.
sync_action = QAction(mw)
sync_action.setText(_(u"S&ync"))
sync_action.setIcon(QIcon(os.path.join(icons_dir, 'sync.png')))
sync_action.setToolTip(_(u"Synchronize with AnkiWeb."))
sync_action.triggered.connect(mw.onSync)
decks_action = QAction(mw)
decks_action.setText(_(u"&Deck browser"))
decks_action.setIcon(QIcon(os.path.join(icons_dir, 'deck_browser.png')))
decks_action.setToolTip(_(u"Go to the deck browser."))
decks_action.triggered.connect(go_deck_browse)
overview_action = QAction(mw)
overview_action.setText(_(u"Deck overview"))
overview_action.setIcon(QIcon(os.path.join(icons_dir, 'study_options.png')))
overview_action.setToolTip(_(u"Go to the deck overview."))
overview_action.triggered.connect(mw.onOverview)
study_action = QAction(mw)
study_action.setText(_(u"Study"))
study_action.setIcon(QIcon(os.path.join(icons_dir, 'study.png')))
study_action.setToolTip(_(u"Start studying the selected deck."))
study_action.triggered.connect(go_study)
add_notes_action = QAction(mw)
add_notes_action.setText(_(u"Add notes"))
add_notes_action.setIcon(QIcon(os.path.join(icons_dir, 'add.png')))
add_notes_action.setToolTip(_(u"Add notes."))
add_notes_action.triggered.connect(mw.onAddCard)
browse_cards_action = QAction(mw)
browse_cards_action.setText(_(u"Browse cards"))
browse_cards_action.setIcon(QIcon(os.path.join(icons_dir, 'browse.png')))
browse_cards_action.setToolTip(_(u"Open the cards browser."))
browse_cards_action.triggered.connect(mw.onBrowse)
statistics_action = QAction(mw)
statistics_action.setText(_(u"Show statistics"))
statistics_action.setIcon(QIcon(os.path.join(icons_dir, 'statistics.png')))
statistics_action.setToolTip(_(u"Show statistics."))
statistics_action.triggered.connect(mw.onStats)
edit_current_action = QAction(mw)
edit_current_action.setText(_(u"Edit current"))
edit_current_action.setIcon(QIcon(os.path.join(icons_dir, 'edit_current.png')))
edit_current_action.setToolTip(_(u"Edit the current note."))
edit_current_action.triggered.connect(go_edit_current)
edit_layout_action = QAction(mw)
edit_layout_action.setText(_(u"Edit layout"))
edit_layout_action.setIcon(QIcon(os.path.join(icons_dir, 'edit_layout.png')))
edit_layout_action.setToolTip(_(u"Edit the layout of the current card."))
edit_layout_action.triggered.connect(go_edit_layout)
toggle_mark_action = QAction(mw)
toggle_mark_action.setText(_(u"Mark"))
toggle_mark_action.setCheckable(True)
toggle_mark_action.setToolTip(_(u"Mark or unmark the current note."))
toggle_mark_icon = QIcon()
toggle_mark_icon.addFile(os.path.join(icons_dir, 'mark_off.png'))
toggle_mark_icon.addFile(
    os.path.join(icons_dir, 'mark_on.png'), QSize(), QIcon.Normal, QIcon.On)
toggle_mark_action.setIcon(toggle_mark_icon)
toggle_mark_action.triggered.connect(mw.reviewer.onMark)
toggle_last_card_action = QAction(mw)
toggle_last_card_action.setText(_(u"Last card"))
toggle_last_card_action.setCheckable(True)
toggle_last_card_action.setChecked(False)
toggle_last_card_action.setToolTip(_(u"Make this card the last to review."))
toggle_last_card_icon = QIcon()
toggle_last_card_icon.addFile(os.path.join(icons_dir, 'last_card_off.png'))
toggle_last_card_icon.addFile(
    os.path.join(icons_dir, 'last_card_on.png'), QSize(), QIcon.Normal,
    QIcon.On)
toggle_last_card_action.setIcon(toggle_last_card_icon)
mute_action = QAction(mw)
mute_action.setText(_(u"Mute"))
mute_action.setCheckable(True)
mute_action.setChecked(config["start_muted"])
mute_action.setToolTip(_(u"Temporarily switch off playing sounds."))
mute_icon = QIcon()
mute_icon.addFile(os.path.join(icons_dir, 'unmute.png'))
mute_icon.addFile(
    os.path.join(icons_dir, 'mute.png'), QSize(), QIcon.Normal, QIcon.On)
mute_action.setIcon(mute_icon)
bury_action = QAction(mw)
bury_action.setText(_(u"Bury note"))
bury_action.setIcon(QIcon(os.path.join(icons_dir, 'bury.png')))
bury_action.setToolTip(_(u"Hide this note for today."))
bury_action.triggered.connect(mw.reviewer.onBuryNote)
suspend_card_action = QAction(mw)
suspend_card_action.setText(_(u"Suspend card"))
suspend_card_action.setIcon(QIcon(os.path.join(icons_dir, 'suspend_card.png')))
suspend_card_action.setToolTip(_(u"Hide this card permanently."))
suspend_card_action.triggered.connect(mw.reviewer.onSuspendCard)
suspend_note_action = QAction(mw)
suspend_note_action.setText(_(u"Suspend note"))
suspend_note_action.setIcon(QIcon(os.path.join(icons_dir, 'suspend.png')))
suspend_note_action.setToolTip(_(u"Hide this note permanently."))
suspend_note_action.triggered.connect(mw.reviewer.onSuspend)
delete_action = QAction(mw)
delete_action.setText(_(u"Delete note"))
delete_action.setIcon(QIcon(os.path.join(icons_dir, 'delete.png')))
delete_action.setToolTip(_(u"Delete this note."))
delete_action.triggered.connect(ask_delete)
options_action = QAction(mw)
options_action.setText(_(u"Study options"))
options_action.setIcon(QIcon(os.path.join(icons_dir, 'options.png')))
options_action.setToolTip(_(u"Show the active study options group."))
options_action.triggered.connect(mw.reviewer.onOptions)
replay_action = QAction(mw)
replay_action.setText(_(u"Replay audio"))
replay_action.setIcon(QIcon(os.path.join(icons_dir, 'replay.png')))
replay_action.setToolTip(_(u"Replay card’s audio or video."))
replay_action.triggered.connect(mw.reviewer.replayAudio)
record_own_action = QAction(mw)
record_own_action.setText(_(u"Record own voice"))
record_own_action.setIcon(QIcon(os.path.join(icons_dir, 'blue_mic.png')))
record_own_action.setToolTip(_(u"Record your own voice."))
record_own_action.triggered.connect(mw.reviewer.onRecordVoice)
replay_own_action = QAction(mw)
replay_own_action.setText(_(u"Replay own voice"))
replay_own_action.setIcon(QIcon(os.path.join(icons_dir, 'play_green.png')))
replay_own_action.setToolTip(_(u"Replay your recorded voice."))
replay_own_action.triggered.connect(mw.reviewer.onReplayRecorded)

## Actions to show and hide the different tool bars.
show_text_toolbar_action = QAction(mw)
show_text_toolbar_action.setText(_(u"Show text tool bar"))
show_text_toolbar_action.setCheckable(True)
show_text_toolbar_action.triggered.connect(toggle_text_toolbar)
show_qt_toolbar_action = QAction(mw)
show_qt_toolbar_action.setText(_(u"Show icon bar"))
show_qt_toolbar_action.setCheckable(True)
show_qt_toolbar_action.setChecked(True)
show_qt_toolbar_action.triggered.connect(toggle_qt_toolbar)
show_more_toolbar_action = QAction(mw)
show_more_toolbar_action.setText(_(u"Show more tool bar"))
show_more_toolbar_action.setCheckable(True)
show_more_toolbar_action.setChecked(True)
show_more_toolbar_action.setEnabled(False)
show_more_toolbar_action.triggered.connect(toggle_more_toolbar)


## Add images to actions we already have. I skip a few where no icon
## really fits.
mw.form.actionDocumentation.setIcon(QIcon(os.path.join(icons_dir, 'help.png')))
mw.form.actionDonate.setIcon(QIcon(os.path.join(icons_dir, 'donate.png')))
mw.form.actionAbout.setIcon(QIcon(os.path.join(icons_dir, 'anki.png')))
mw.form.actionUndo.setIcon(QIcon(os.path.join(icons_dir, 'undo.png')))
mw.form.actionSwitchProfile.setIcon(
    QIcon(os.path.join(icons_dir, 'switch-profile.png')))
mw.form.actionImport.setIcon(QIcon(os.path.join(icons_dir, 'import.png')))
mw.form.actionExport.setIcon(QIcon(os.path.join(icons_dir, 'export.png')))
mw.form.actionExit.setIcon(QIcon(os.path.join(icons_dir, 'exit.png')))
mw.form.actionDownloadSharedPlugin.setIcon(
    QIcon(os.path.join(icons_dir, 'download-addon.png')))
mw.form.actionFullDatabaseCheck.setIcon(
    QIcon(os.path.join(icons_dir, 'check-db.png')))
mw.form.actionPreferences.setIcon(
    QIcon(os.path.join(icons_dir, 'preferences.png')))

## Hide the edit and nmore buttons.
# mw.reviewer._bottomCSS += "td.stat button {display:none;}"
#mw.reviewer.bottom.css += "td.stat button {display:none;}"


# Create the menus
add_toolbar()
add_more_toolbar()
add_to_menus()
#mw.toolbar.web.hide()


# Mid level wrappers to do stuff for the wrapped methods.
def deck_browser_show_extras(dummy_deck_browser):
    edit_actions_off()
    more_toolbar_off()


def overview_show_extras(dummy_overview):
    more_toolbar_off()
    edit_actions_on()


def reviewer_show_extras(dummy_reviewer):
    edit_actions_on()
    maybe_more_toolbar_on()

def draw_no_star(dummy_reviewer):
    pass


DeckBrowser.show = wrap(DeckBrowser.show, deck_browser_show_extras)
Overview.show = wrap(Overview.show, overview_show_extras)
Reviewer.show = wrap(Reviewer.show, reviewer_show_extras)
# TODO: Check the mark stuff
# Reviewer._toggleStar = wrap(Reviewer._toggleStar, update_mark_action)
Reviewer._drawMark = draw_no_star


# Wrapper to not show a next card.
original_next_card = Reviewer.nextCard
Reviewer.nextCard = next_card_wrapper
Reviewer.autoplay = maybe_autoplay

# Make sure we don't leave a stale last card button switched on
addHook("reviewCleanup", next_card_toggle_off)

addHook("unloadProfile", save_toolbars_visible)
addHook("profileLoaded", load_toolbars_visible)
