# Change Log

### July 20, 2022 - v2.4

* Fixed inability to discard a power card from public card page
* Fixed inability to set number of uses on public card page
* Upped number of use limit to 7
* Do not deal power cards to inactive players on new game
* Added guard code around card transfer to try and fix problem where card disappears when dragging

### July 11, 2022 - v2.3

* Player instructions field always enabled
* Clear out orb and num uses card fields on new games
* Fixed code issue with use of BaseCard vs Card
* Clear program hand and registers when out of game

### June 20, 2022 - v2.2

* Added API route to deal new program hand for a player
* Fixed discard power card bug on public card page
### May 31, 2022 - v2.1

* Added number of uses and orb fields to power cards
* DB migration to support the above
* Fixed JSON encoding issue

### April 17, 2022 - v2.0

* Remove power played hand
* Adding drag and drop to public card page

### March 24, 2022 - v1.6

* Fixed disable issue on player page related to powering down
* Make power down/up more obvious on player page
* Changed all instances of "round" to "turn"

### March 16, 2022 - v1.5

* Fix shuffling again by limit cut indexes
* Fix register numbering on player age
* Headers on public card page

### March 7, 2022 - v1.4

* Fix shuffling by adding random cut in between
* Enforce max of two power cards in UI
* Add power card max in entities, but don't enforce yet
* Only show active players in public card page
* Add flashes for drawing cards in turn page

### February 23, 2022 - v1.3

* Show all power cards on public page
* Draw three power cards on new game instad of one
* Fix minimum number of deck shuffles
* Don't show excluded people in turn warning page
* Don't reset active flag on new turn

### February 18, 2022 - v1.2

Add ability to exclude players from game

### February 14, 2022 - v1.1

* Drag and drop on mobile
* Add note area to board state
* Make publicly viewable card page

### January 11, 2022 - v1.0

* Added version number
* Draw power card on new game