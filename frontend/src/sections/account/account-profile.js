import {
  Avatar,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Divider,
  Typography
} from '@mui/material';


// const user = {
//   avatar: '/assets/avatars/avatar-anika-visser.png',
//   city: 'Los Angeles',
//   country: 'USA',
//   jobTitle: 'Senior Developer',
//   name: 'Anika Visser',
//   timezone: 'GTM-7'
// };

const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users/me`, {
  method: 'GET',
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + Cookies.get("token")
  },
});
const user = await res.json();

export const AccountProfile = () => (
  <Card>
    <CardContent>
      <Box
        sx={{
          alignItems: 'center',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <Avatar
          src={user.avatar}
          sx={{
            height: 80,
            mb: 2,
            width: 80
          }}
        />
        <Typography
          gutterBottom
          variant="h5"
        >
          {user.name}
        </Typography>
        <Typography
          color="text.secondary"
          variant="body2"
        >
          {user.city} {user.country}
        </Typography>
        <Typography
          color="text.secondary"
          variant="body2"
        >
          {user.timezone}
        </Typography>
      </Box>
    </CardContent>
    <Divider />
    <CardActions>
      <Button
        fullWidth
        variant="text"
      >
        Upload picture
      </Button>
    </CardActions>
  </Card>
);
