from abc import abstractmethod
from typing import Optional

from leeger.exception.DoesNotExistException import DoesNotExistException
from leeger.model.league.League import League
from leeger.model.league.Owner import Owner


class LeagueLoader:
    """
    League Loader classes should inherit this.
    The point of a test_league loader is to load a League object from different Fantasy Football sources.
    """

    def __init__(self, leagueId: str | str, years: list[int] = None, **kwargs):
        self._leagueId = leagueId
        self._years = years
        self._owners: Optional[list[Owner]] = None
        # owners may have multiple names across different years,
        # defining owner names and aliases allows users to have multiple names that can belong to the same owner.
        # this prevents issues where an owner with a name change across years is counted as 2 different owners.
        # this should be formatted like so:
        # ownerNamesAndAliases = {"someOwnerNameIWant": ["alias1", "alias2"],
        #                           someOtherOwnerNameIWant: ["alias3", "alias4"]}
        self._ownerNamesAndAliases = kwargs.get("ownerNamesAndAliases", dict())

    def _getGeneralOwnerNameFromGivenOwnerName(self, givenOwnerName: str) -> Optional[str]:
        foundGeneralOwnerName = None
        for generalOwnerName, aliases in self._ownerNamesAndAliases.items():
            if givenOwnerName in aliases:
                foundGeneralOwnerName = generalOwnerName
                break
        return foundGeneralOwnerName

    def _getOwnerByName(self, ownerName: str) -> Owner:
        generalOwnerName = self._getGeneralOwnerNameFromGivenOwnerName(ownerName)
        for owner in self._owners:
            if ownerName == owner.name or generalOwnerName == owner.name:
                return owner
        raise DoesNotExistException(
            f"Owner name '{ownerName}' does not match any previously loaded owner names. To add multiple names for a single owner, use the 'ownerNamesAndAliases' keyword argument to define them.")

    @abstractmethod
    def loadLeague(self, *args, **kwargs) -> League:
        ...
