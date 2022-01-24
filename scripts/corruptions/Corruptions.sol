// SPDX-License-Identifier: Unlicense

/*
    $$8$$$8$$$$$$$88$$$$$$$$8$8$$$$
    8...................8..8......$
    $.8......88.......8.......8...$
    $..88.......8CC8CC............$
    $8.........C88OOO8CC......8..8$
    $8.8.....88OOR8RRR8OCC8....8..$
    $.......C.ORRRRRRRRRO.C....8..$
    $....8.C.88RRUUUUURRRO.C.8....$
    $8...8C.8RR.UP8PPPU.RRO.C.....$
    $.8..8.OR8.88.T88.PU.RRO.88...$
    $...8CO8R.UPTTI8I8TP8.RROC.8.8$
    $...CO8R.UPT.IOOO8.TPU.RROC..8$
    $.88CORRUP8.IO8N8OI.TPURR8C8..$
    $..C8RR8P.TION.8.8OIT.P8RROC..$
    $.8COR8UP8ION..8..NOIT8URROC..$
    8..CORRUPTION..8..NOI8PURRO8..$
    $.88ORRUP8ION.....8OITPU8ROC..$
    $..CORRUP.TION...NOIT.PURR8C..$
    $...COR8UPT.I8N8NOI.TP8RROC..8$
    $...COR8.U8T8IOO8I.TPU8RROC...$
    $8...C88R.UPTTIII8888.RROC..8.$
    $8.8.C.ORR.8P.TT88PU.RRO.C8...$
    $.8...C.ORR.UPP8PP8.R8O.C...8.$
    $......C.8R88UUUU8RRRO.C8....8$
    8.......C.OR8RRRRRRRO.C.......$
    $....8.8.CCOORRRR888CC...88...$
    $..........CCOO8OOCC..........$
    $........88..CCC8C..8.........$
    88.8......8.............88....$
    $.....................88..88..$
    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

    unfine art by dom

    1/ 4,196 corruptions
    1/ corruptions gain insight over time
    1/ insight accelerates if a corruption is stabilized (left alone)
    1/ insight decelerates if a corruption is destabilized (moved)
*/

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./CorruptionsMetadata.sol";

contract Corruptions is ERC721Enumerable,  ReentrancyGuard, Ownable {
    event Claimed(uint256 index, address account, uint256 amount);

    address public metadataAddress;

    bool public tradable;
    bool public claimable;

    uint256 private maxMultiplier;

    struct XP {
        uint256 savedXP;
        uint256 lastSaveBlock;
    }

    mapping (uint256 => XP) public insightMap;

    uint256 private balance;

    modifier onlyWhenTradable() {
        require(tradable, "Corruptions: cannot trade");
        _;
    }

    constructor() ERC721("Corruptions", "CORRUPT") Ownable() {
        tradable = true;
        maxMultiplier = 24;
    }

    function setMetadataAddress(address addr) public onlyOwner {
        metadataAddress = addr;
    }

    function setTradability(bool tradability) public onlyOwner {
        tradable = tradability;
    }

    function setClaimability(bool claimability) public onlyOwner {
        claimable = claimability;
    }

    function setMaxMultiplier(uint256 multiplier) public onlyOwner {
        maxMultiplier = multiplier;
    }

    function insight(uint256 tokenID) public view returns (uint256) {
        uint256 lastBlock = insightMap[tokenID].lastSaveBlock;
        if (lastBlock == 0) {
            return 0;
        }
        uint256 delta = block.number - lastBlock;
        uint256 multiplier = delta / 200000;
        if (multiplier > maxMultiplier) {
            multiplier = maxMultiplier;
        }
        uint256 total = insightMap[tokenID].savedXP + (delta * (multiplier + 1) / 10000);
        if (total < 1) total = 1;

        return total;
    }

    function save(uint256 tokenID) private {
        insightMap[tokenID].savedXP = insight(tokenID);
        insightMap[tokenID].lastSaveBlock = block.number;
    }

    function tokenURI(uint256 tokenID) override public view returns (string memory) {
        require(metadataAddress != address(0), "Corruptions: no metadata address");
        require(tokenID < totalSupply(), "Corruptions: token doesn't exist");
        return ICorruptionsMetadata(metadataAddress).tokenURI(tokenID, insight(tokenID));
    }

    function transferFrom(address from, address to, uint256 tokenId) public override onlyWhenTradable {
        super.transferFrom(from, to, tokenId);
    }

    function safeTransferFrom(address from, address to, uint256 tokenId) public override onlyWhenTradable {
        super.safeTransferFrom(from, to, tokenId);
    }

    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public override onlyWhenTradable {
        super.safeTransferFrom(from, to, tokenId, _data);
    }

    function approve(address to, uint256 tokenId) public override onlyWhenTradable {
        super.approve(to, tokenId);
    }

    function setApprovalForAll(address operator, bool approved) public override onlyWhenTradable {
        super.setApprovalForAll(operator, approved);
    }

    function _beforeTokenTransfer(address from, address to, uint256 tokenId) internal override {
        super._beforeTokenTransfer(from, to, tokenId);

        save(tokenId);
    }

    function EXPERIMENTAL_UNAUDITED_NO_ROADMAP_ABSOLUTELY_NO_PROMISES_BUT_I_ACKNOWLEDGE_AND_WANT_TO_MINT_ANYWAY() payable public nonReentrant {
        require(msg.value == 0.08 ether, "Corruptions: 0.08 ETH to mint");
        require(claimable || _msgSender() == owner(), "Corruptions: cannot claim");
        require(totalSupply() < 4196, "Corruptions: all claimed");
        _mint(_msgSender(), totalSupply());

        balance += 0.08 ether;
    }

    function withdrawAvailableBalance() public nonReentrant onlyOwner {
        uint256 b = balance;
        balance = 0;
        payable(msg.sender).transfer(b);
    }
}